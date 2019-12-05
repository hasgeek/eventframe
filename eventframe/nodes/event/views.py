# -*- coding: utf-8 -*-

from io import StringIO
import unicodecsv
from werkzeug.routing import Map as UrlMap, Rule as UrlRule
from flask import request, render_template, abort, Markup, flash, redirect, escape, jsonify
from flask_themes import get_theme, render_theme_template
from coaster.auth import current_auth
from eventframe import lastuser
from eventframe.forms import ConfirmForm
from eventframe.nodes import db, NodeHandler
from eventframe.nodes.content import ContentHandler
from eventframe.nodes.map import Map
from eventframe.nodes.participant_list import ParticipantList
from eventframe.nodes.event.models import Event
from eventframe.nodes.event.forms import EventForm

__all__ = ['EventHandler', 'EventViewHandler', 'register']


class EventHandler(ContentHandler):
    form_class = EventForm
    model = Event
    title_new = "New event"
    title_edit = "Edit event"

    actions = ['list', 'csv', 'update', 'json']

    def edit_tabs(self):
        tabs = super(EventHandler, self).edit_tabs()
        if self.node:
            tabs = tabs + [
                {'title': "Attendees", 'url': self.node.url_for('list'), 'active': self.action == 'list'},
                ]
        return tabs

    def make_form(self):
        form = super(EventHandler, self).make_form()
        form.map.query_factory = lambda: Map.query.filter_by(folder=self.folder)
        form.participant_list.query_factory = lambda: ParticipantList.query.filter_by(folder=self.folder)
        if request.method == 'GET':
            if self.node:
                form.start_datetime.data = self.node.start_datetime
                form.end_datetime.data = self.node.end_datetime
                form.timezone.data = self.node.timezone
                form.location_name.data = self.node.location_name
                form.location_address.data = self.node.location_address
                form.map.data = self.node.map
                form.mapmarker.data = self.node.mapmarker
                form.capacity.data = self.node.capacity
                form.allow_waitlisting.data = self.node.allow_waitlisting
                form.allow_maybe.data = self.node.allow_maybe
                form.participant_list.data = self.node.participant_list
            else:
                form.template.data = 'event.html.jinja2'
        return form

    def process_node(self):
        self.node.start_datetime = self.form.start_datetime.data
        self.node.end_datetime = self.form.end_datetime.data
        self.node.timezone = self.form.timezone.data
        self.node.location_name = self.form.location_name.data
        self.node.location_address = self.form.location_address.data
        self.node.map = self.form.map.data
        self.node.mapmarker = self.form.mapmarker.data
        self.node.capacity = self.form.capacity.data
        self.node.allow_waitlisting = self.form.allow_waitlisting.data
        self.node.allow_maybe = self.form.allow_maybe.data
        self.node.participant_list = self.form.participant_list.data

    def list(self):
        self.action = 'list'
        self.form = None
        attendees = self.node.attendees
        attendees.sort(key=lambda a: ({'Y': 0, 'M': 1, 'W': 2, 'N': 3}.get(a.status), a.user.fullname.strip().upper()))
        return render_template('event_attendees.html.jinja2', node=self.node, attendees=attendees, tabs=self.edit_tabs())

    def csv(self):
        f = StringIO()
        out = unicodecsv.writer(f, encoding='utf-8')
        out.writerow(['Name', 'Email', 'Status'])
        attendees = self.node.attendees
        attendees.sort(key=lambda a: ({'Y': 0, 'M': 1, 'W': 2, 'N': 3}.get(a.status), a.user.fullname.strip().upper()))
        for attendee in attendees:
            out.writerow([attendee.user.fullname, attendee.user.email, attendee.status])
        f.seek(0)
        return f.getvalue(), 200, [
            ('Content-Type', 'text/csv; charset=utf-8'),
            ('Content-Disposition', 'attachment; filename=' + self.node.name + '.csv')]

    def json(self):
        data = []
        attendees = self.node.attendees
        attendees.sort(key=lambda a: ({'Y': 0, 'M': 1, 'W': 2, 'N': 3}.get(a.status), a.user.fullname.strip().upper()))
        for attendee in attendees:
            if self.node.participant_list:
                participant = self.node.participant_list.get_participant(attendee.user)
            else:
                participant = None
            adata = {
                'fullname': attendee.user.fullname,
                'email': attendee.user.email,
                'status': attendee.status,
                }
            if participant:
                adata.update({
                    'ticket': participant.ticket,
                    'ticket_name': participant.fullname,
                    'ticket_email': participant.email,
                    'ticket_phone': participant.phone,
                    'ticket_twitter': participant.twitter,
                    'ticket_type': participant.ticket_type,
                    'ticket_jobtitle': participant.jobtitle,
                    'ticket_company': participant.company,
                    'ticket_city': participant.city,
                    'ticket_tshirt_size': participant.tshirt_size,
                    })
            data.append(adata)
        return jsonify(attendees=data)

    def update(self):
        # FIXME: Shouldn't be a GET request
        for attendee in self.node.attendees:
            lastuser.update_user(attendee.user)
        db.session.commit()
        flash("User details updated", 'success')
        return redirect(self.node.url_for('list'), code=303)


class EventViewHandler(NodeHandler):
    def GET(self):
        form = ConfirmForm()
        theme = get_theme(self.folder.theme)
        return render_theme_template(theme, self.node.template,
            website=self.website, folder=self.folder, title=self.node.title, node=self.node,
            form=form, _fallback=False)

    def rsvp(self):
        form = ConfirmForm()
        if not form.validate_on_submit():
            if request.is_xhr:
                return Markup('<div class="alert alert-error">An error occured. Please reload the page and try again.</div>>')
            else:
                flash("An error occured. Please try again.", category='error')
                return redirect(self.node.url_for('view'), code=303)
        if current_auth.is_anonymous:
            if request.is_xhr:
                return Markup('<div class="alert alert-error">You are not logged in</div>')
            else:
                abort(403)
        status = request.form.get('status')
        # All good. Set status for this user.
        try:
            self.node.set_status(current_auth.user, status)
        except ValueError as e:
            if request.is_xhr:
                return Markup('<div class="alert alert-error">%s</div>' % escape(str(e)))
            else:
                abort(403)
        db.session.commit()
        if request.is_xhr:
            return Markup('<div class="alert alert-success">Your response has been recorded.</div>')
        else:
            flash("Your response has been recorded.", category='success')
            return redirect(self.node.url_for('view'), code=303)

url_map = UrlMap([
    UrlRule('/rsvp', endpoint='rsvp', methods=['POST'])
    ])


def register(registry):
    registry.register(Event, EventHandler, view_handler=EventViewHandler, view_url_map=url_map, render=True)
