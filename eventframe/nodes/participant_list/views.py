# -*- coding: utf-8 -*-

import requests
from flask import request, Response, stream_with_context, url_for, render_template
from coaster.utils import parse_isoformat
from eventframe import eventapp, lastuser
from eventframe.signals import signal_login
from eventframe.forms import ConfirmForm
from eventframe.nodes import db, render_form, stream_template
from eventframe.nodes.content import ContentHandler
from eventframe.nodes.participant_list.models import ParticipantList, Participant
from eventframe.nodes.participant_list.forms import ParticipantListForm

__all__ = ['ParticipantListHandler', 'register']


# TODO: Implement view handler and url_map
class ParticipantListHandler(ContentHandler):
    form_class = ParticipantListForm
    model = ParticipantList
    title_new = u"New participant list"
    title_edit = u"Edit participant list"

    actions = ['sync', 'list']

    def edit_tabs(self):
        tabs = super(ParticipantListHandler, self).edit_tabs()
        if self.node:
            tabs = tabs + [
                {'title': u"List", 'url': self.node.url_for('list'), 'active': self.action == 'list'},
                {'title': u"Sync", 'url': self.node.url_for('sync'), 'active': self.action == 'sync'},
                ]
        return tabs

    def make_form(self):
        form = super(ParticipantListHandler, self).make_form()
        if request.method == 'GET':
            if self.node:
                form.source.data = self.node.source
                form.sourceid.data = self.node.sourceid
                form.api_key.data = self.node.api_key
                form.participant_template.data = self.node.participant_template
            else:
                form.template.data = 'directory.html.jinja2'
        return form

    def process_node(self):
        self.node.source = self.form.source.data
        self.node.sourceid = self.form.sourceid.data
        self.node.api_key = self.form.api_key.data
        self.node.participant_template = self.form.participant_template.data

    def list(self):
        self.action = 'list'
        self.form = None
        participants = self.node.participants
        participants.sort(key=lambda p: p.fullname.strip().upper())
        return render_template('participant_list.html.jinja2', node=self.node, participants=participants, tabs=self.edit_tabs())

    def sync(self):
        self.action = 'sync'
        self.form = ConfirmForm()

        if self.form.validate_on_submit():
            return Response(stream_template('stream.html.jinja2',
                stream=stream_with_context(self._sync()),
                tabs=self.edit_tabs(),
                node=self.node,
                title="Syncing participants..."))

        return render_form(form=self.form, title="Sync participant list", submit=u"Sync", tabs=self.edit_tabs(),
        cancel_url=url_for('folder', website=self.node.folder.website.name, folder=self.node.folder.name),
        node=self.node)

    def _sync(self):
        if self.node.source != 'doattend':
            yield "Unsupported data source, aborting.\n"
            return
        if not self.node.sourceid or not self.node.api_key:
            yield "Source event id and API key are required.\n"
            return
        # All good, start pulling data...
        data_url = 'http://doattend.com/api/events/%s/participants_list.json?api_key=%s' % (
            self.node.sourceid, self.node.api_key)
        yield "Receiving data from DoAttend..."
        r = requests.get(data_url)
        data = r.json() if callable(r.json) else r.json
        yield " OK\n"
        yield "Participant count: %d\n" % len(data['participants'])
        yield "Previously synced count: %d\n\n" % len(self.node.participants)

        by_ticket = {}
        local_tickets = set()
        upstream_tickets = set()
        unindexed = []
        for participant in self.node.participants:
            if participant.ticket is not None:
                by_ticket[participant.ticket] = participant
                local_tickets.add(participant.ticket)
            else:
                unindexed.append(participant)
        plist = data['participants']
        plist.reverse()  # DoAttend list is sorted by most-recent first
        for p in plist:
            upstream_tickets.add(p['Ticket_Number'])
            participant = by_ticket.get(p['Ticket_Number'])
            if participant is None:
                participant = Participant(participant_list=self.node)
                db.session.add(participant)
                participant.ticket = p['Ticket_Number'].strip()
                by_ticket[participant.ticket] = participant
                local_tickets.add(participant.ticket)
            syncinfo = {
                'datetime': parse_isoformat(p['Date']),
                'fullname': p['Name'].strip() if isinstance(p['Name'], basestring) else p['Name'],
                'email': p['Email'].strip() if isinstance(p['Email'], basestring) else p['Email'],
                'ticket_type': p['Ticket_Name'].strip() if isinstance(p['Ticket_Name'], basestring) else p['Ticket_Name'],
            }
            pinfo = p.get('participant_information', [])
            if isinstance(pinfo, dict):
                pinfo = [pinfo]
            for keyval in pinfo:
                key = keyval['desc']
                value = keyval.get('info')
                if key == 'Job Title':
                    syncinfo['jobtitle'] = value.strip() if isinstance(value, basestring) else value
                elif key == 'Company':
                    syncinfo['company'] = value.strip() if isinstance(value, basestring) else value
                elif key == 'Twitter Handle':
                    syncinfo['twitter'] = value.strip() if isinstance(value, basestring) else value
                elif key == 'City':
                    syncinfo['city'] = value.strip() if isinstance(value, basestring) else value
                elif key == 'T-shirt size':
                    syncinfo['tshirt_size'] = value.split('-', 1)[0].strip() if isinstance(value, basestring) else value
            edited = False
            for key, value in syncinfo.items():
                if getattr(participant, key) != value:
                    setattr(participant, key, value)
                    if 'key' == 'email':
                        participant.user = None
                    edited = True
            if edited:
                if participant.id is None:
                    yield "New participant (#%s): %s\n" % (participant.ticket, participant.fullname)
                else:
                    yield "Edited participant (#%s): %s\n" % (participant.ticket, participant.fullname)
        # Check for deleted participants
        removed_tickets = local_tickets - upstream_tickets
        for ticket in removed_tickets:
            participant = by_ticket.get(ticket)
            if participant:
                yield "Removed participant (#%s): %s\n" % (ticket, participant.fullname)
                db.session.delete(participant)
        db.session.commit()
        yield '\nAll done.'


@signal_login.connect_via(eventapp)
def login_watcher(sender, user, **kwargs):
    emails = lastuser.user_emails(user)
    # Find all Participant records that have a matching email address and link them to this user
    if emails:
        participants = Participant.query.filter(Participant.email.in_(emails)).all()
        # Link user to participants
        for p in participants:
            if p.user != user:
                p.user = user


def register(registry):
    registry.register(ParticipantList, ParticipantListHandler, render=True)
