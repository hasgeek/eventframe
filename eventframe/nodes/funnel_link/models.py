# -*- coding: utf-8 -*-

from datetime import datetime
import requests
from requests.exceptions import ConnectionError
from eventframe.nodes import db, Node
from eventframe.nodes.content import ContentMixin

__all__ = ['FunnelLink']


class FunnelLink(ContentMixin, Node):
    __tablename__ = 'funnel_link'
    funnel_name = db.Column(db.Unicode(80), nullable=False)

    def as_json(self):
        result = super(FunnelLink, self).as_json()
        result.update({'funnel_name': self.funnel_name})
        return result

    def import_from(self, data):
        super(FunnelLink, self).import_from(data)
        self.funnel_name = data['funnel_name']

    def _data(self):
        if not hasattr(self, '_data_cached'):
            # Get JSON and cache locally
            try:
                r = requests.get('http://funnel.hasgeek.com/%s/json' % self.funnel_name)
                data = r.json() if callable(r.json) else r.json
                sectionmap = dict([(s['title'], s['name']) for s in data['sections']])
                for proposal in data['proposals']:
                    proposal['submitted'] = datetime.strptime(proposal['submitted'], '%Y-%m-%dT%H:%M:%SZ')
                    proposal['section_name'] = sectionmap.get(proposal['section'])
                    v = proposal['votes']
                    proposal['votes'] = '+%d' % v if v > 0 else '%d' % v
                self._data_cached = data
            except ConnectionError:
                self._data_cached = {
                    'proposals': [],
                    'sections': [],
                    'space': {},
                }
        return self._data_cached

    def proposals_mapping(self):
        if not hasattr(self, '_dict_cached'):
            self._dict_cached = dict([(p['id'], p) for p in self.proposals()])
        return self._dict_cached

    def sections(self):
        # Get data from Funnel and cache locally
        return self._data()['sections']

    def proposals(self):
        return self._data()['proposals']

    def confirmed(self):
        return [p for p in self._data()['proposals'] if p['confirmed']]
