# -*- coding: utf-8 -*-

# Import models and make them available here
from eventframe.models import db, BaseMixin, BaseScopedNameMixin
from eventframe.models.user import User
from eventframe.models.website import Website, Folder, Node, NodeMixin, default_user_id
from eventframe.nodes.helpers import *

import eventframe.nodes.data
import eventframe.nodes.event
import eventframe.nodes.fragment
import eventframe.nodes.funnel_link
import eventframe.nodes.list
import eventframe.nodes.map
import eventframe.nodes.page
import eventframe.nodes.participant_list
import eventframe.nodes.post
import eventframe.nodes.redirect


# Register nodes. The sequence here is preserved in the New Node dropdown in the UI
def init():
    eventframe.nodes.page.register(node_registry)
    eventframe.nodes.post.register(node_registry)
    eventframe.nodes.fragment.register(node_registry)
    eventframe.nodes.redirect.register(node_registry)
    eventframe.nodes.data.register(node_registry)
    eventframe.nodes.funnel_link.register(node_registry)
    eventframe.nodes.event.register(node_registry)
    eventframe.nodes.list.register(node_registry)
    eventframe.nodes.map.register(node_registry)
    eventframe.nodes.participant_list.register(node_registry)
