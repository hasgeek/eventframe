"""Init

Revision ID: 4223247fce24
Revises: None
Create Date: 2015-12-10 17:01:21.404837

"""

# revision identifiers, used by Alembic.
revision = '4223247fce24'
down_revision = None

from alembic import op
import sqlalchemy as sa
import coaster.sqlalchemy


def upgrade():
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('lastuser_token_scope', sa.Unicode(length=250), nullable=True),
        sa.Column('lastuser_token_type', sa.Unicode(length=250), nullable=True),
        sa.Column('userinfo', coaster.sqlalchemy.JsonDict(), nullable=True),
        sa.Column('email', sa.Unicode(length=80), nullable=True),
        sa.Column('lastuser_token', sa.String(length=22), nullable=True),
        sa.Column('username', sa.Unicode(length=80), nullable=True),
        sa.Column('userid', sa.String(length=22), nullable=False),
        sa.Column('fullname', sa.Unicode(length=80), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('lastuser_token'),
        sa.UniqueConstraint('userid'),
        sa.UniqueConstraint('username')
        )
    op.create_table('website',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('url', sa.Unicode(length=80), nullable=False),
        sa.Column('theme', sa.Unicode(length=80), nullable=False),
        sa.Column('typekit_code', sa.Unicode(length=20), nullable=False),
        sa.Column('googleanalytics_code', sa.Unicode(length=20), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
        )
    op.create_table('content_revision',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=False),
        sa.Column('previous_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('description', sa.UnicodeText(), nullable=False),
        sa.Column('content', sa.UnicodeText(), nullable=False),
        sa.Column('template', sa.Unicode(length=80), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['revisions.id'], name='fk_content_revision_parent_id', use_alter=True),
        sa.ForeignKeyConstraint(['previous_id'], ['content_revision.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('folder',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('website_id', sa.Integer(), nullable=False),
        sa.Column('theme', sa.Unicode(length=80), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.ForeignKeyConstraint(['website_id'], ['website.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'website_id')
        )
    op.create_table('hostname',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('website_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['website_id'], ['website.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
        )
    op.create_table('logincode',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('code', sa.Unicode(length=22), nullable=False),
        sa.Column('scope', sa.Unicode(length=250), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('next_url', sa.Unicode(length=250), nullable=False),
        sa.Column('return_url', sa.Unicode(length=250), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
        )
    op.create_table('node',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('uuid', sa.Unicode(length=22), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('author', sa.Unicode(length=40), nullable=True),
        sa.Column('folder_id', sa.Integer(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('type', sa.Unicode(length=20), nullable=True),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.ForeignKeyConstraint(['folder_id'], ['folder.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'folder_id'),
        sa.UniqueConstraint('uuid')
        )
    op.create_table('revisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('published_id', sa.Integer(), nullable=True),
        sa.Column('draft_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['draft_id'], ['content_revision.id'], ),
        sa.ForeignKeyConstraint(['published_id'], ['content_revision.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('data',
        sa.Column('data', coaster.sqlalchemy.JsonDict(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['node.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('fragment',
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('revisions_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['node.id'], ),
        sa.ForeignKeyConstraint(['revisions_id'], ['revisions.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_index(op.f('ix_fragment_published'), 'fragment', ['published'], unique=False)
    op.create_table('funnel_link',
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('funnel_name', sa.Unicode(length=80), nullable=False),
        sa.Column('revisions_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['node.id'], ),
        sa.ForeignKeyConstraint(['revisions_id'], ['revisions.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_index(op.f('ix_funnel_link_published'), 'funnel_link', ['published'], unique=False)
    op.create_table('list',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['node.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('map',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['node.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('page',
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('revisions_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['node.id'], ),
        sa.ForeignKeyConstraint(['revisions_id'], ['revisions.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_index(op.f('ix_page_published'), 'page', ['published'], unique=False)
    op.create_table('participant_list',
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('source', sa.Unicode(length=80), nullable=False),
        sa.Column('sourceid', sa.Unicode(length=80), nullable=False),
        sa.Column('api_key', sa.Unicode(length=80), nullable=False),
        sa.Column('participant_template', sa.Unicode(length=80), nullable=False),
        sa.Column('revisions_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['node.id'], ),
        sa.ForeignKeyConstraint(['revisions_id'], ['revisions.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_index(op.f('ix_participant_list_published'), 'participant_list', ['published'], unique=False)
    op.create_table('post',
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('revisions_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['node.id'], ),
        sa.ForeignKeyConstraint(['revisions_id'], ['revisions.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_index(op.f('ix_post_published'), 'post', ['published'], unique=False)
    op.create_table('property',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('node_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=40), nullable=False),
        sa.Column('value', sa.Unicode(length=250), nullable=False),
        sa.ForeignKeyConstraint(['node_id'], ['node.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'node_id')
        )
    op.create_table('redirect',
        sa.Column('redirect_url', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['node.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('event',
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('start_datetime', sa.DateTime(), nullable=False),
        sa.Column('end_datetime', sa.DateTime(), nullable=False),
        sa.Column('timezone', sa.Unicode(length=32), nullable=False),
        sa.Column('location_name', sa.Unicode(length=80), nullable=False),
        sa.Column('location_address', sa.Unicode(length=250), nullable=False),
        sa.Column('map_id', sa.Integer(), nullable=True),
        sa.Column('mapmarker', sa.Unicode(length=80), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('allow_waitlisting', sa.Boolean(), nullable=False),
        sa.Column('allow_maybe', sa.Boolean(), nullable=False),
        sa.Column('participant_list_id', sa.Integer(), nullable=True),
        sa.Column('revisions_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['node.id'], ),
        sa.ForeignKeyConstraint(['map_id'], ['map.id'], ),
        sa.ForeignKeyConstraint(['participant_list_id'], ['participant_list.id'], ),
        sa.ForeignKeyConstraint(['revisions_id'], ['revisions.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_index(op.f('ix_event_published'), 'event', ['published'], unique=False)
    op.create_table('list_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('list_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=80), nullable=True),
        sa.Column('title', sa.Unicode(length=250), nullable=True),
        sa.Column('url', sa.Unicode(length=250), nullable=True),
        sa.Column('node_id', sa.Integer(), nullable=True),
        sa.Column('seq', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['list_id'], ['list.id'], ),
        sa.ForeignKeyConstraint(['node_id'], ['node.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('list_id', 'name'),
        sa.UniqueConstraint('list_id', 'node_id')
        )
    op.create_table('map_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('map_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.Unicode(length=250), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=7, scale=4), nullable=False),
        sa.Column('longitude', sa.Numeric(precision=7, scale=4), nullable=False),
        sa.Column('zoomlevel', sa.Integer(), nullable=True),
        sa.Column('marker', sa.Unicode(length=80), nullable=True),
        sa.Column('seq', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.ForeignKeyConstraint(['map_id'], ['map.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('map_id', 'name')
        )
    op.create_table('participant',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('participant_list_id', sa.Integer(), nullable=False),
        sa.Column('datetime', sa.DateTime(), nullable=True),
        sa.Column('ticket', sa.Unicode(length=80), nullable=True),
        sa.Column('fullname', sa.Unicode(length=80), nullable=True),
        sa.Column('email', sa.Unicode(length=80), nullable=True),
        sa.Column('phone', sa.Unicode(length=80), nullable=True),
        sa.Column('twitter', sa.Unicode(length=80), nullable=True),
        sa.Column('ticket_type', sa.Unicode(length=80), nullable=True),
        sa.Column('jobtitle', sa.Unicode(length=80), nullable=True),
        sa.Column('company', sa.Unicode(length=80), nullable=True),
        sa.Column('city', sa.Unicode(length=80), nullable=True),
        sa.Column('tshirt_size', sa.Unicode(length=4), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('access_key', sa.Unicode(length=44), nullable=True),
        sa.Column('is_listed', sa.Boolean(), nullable=False),
        sa.Column('fields_directory', sa.Unicode(length=250), nullable=False),
        sa.Column('fields_contactpoint', sa.Unicode(length=250), nullable=False),
        sa.ForeignKeyConstraint(['participant_list_id'], ['participant_list.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('access_key'),
        sa.UniqueConstraint('ticket')
        )
    op.create_table('event_attendee',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Unicode(length=1), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'event_id')
        )


def downgrade():
    op.drop_table('event_attendee')
    op.drop_table('participant')
    op.drop_table('map_item')
    op.drop_table('list_item')
    op.drop_index(op.f('ix_event_published'), table_name='event')
    op.drop_table('event')
    op.drop_table('redirect')
    op.drop_table('property')
    op.drop_index(op.f('ix_post_published'), table_name='post')
    op.drop_table('post')
    op.drop_index(op.f('ix_participant_list_published'), table_name='participant_list')
    op.drop_table('participant_list')
    op.drop_index(op.f('ix_page_published'), table_name='page')
    op.drop_table('page')
    op.drop_table('map')
    op.drop_table('list')
    op.drop_index(op.f('ix_funnel_link_published'), table_name='funnel_link')
    op.drop_table('funnel_link')
    op.drop_index(op.f('ix_fragment_published'), table_name='fragment')
    op.drop_table('fragment')
    op.drop_table('data')
    op.drop_table('revisions')
    op.drop_table('node')
    op.drop_table('logincode')
    op.drop_table('hostname')
    op.drop_table('folder')
    op.drop_table('content_revision')
    op.drop_table('website')
    op.drop_table('user')
