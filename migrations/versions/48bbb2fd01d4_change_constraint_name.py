"""Change constraint name

Revision ID: 48bbb2fd01d4
Revises: 4223247fce24
Create Date: 2015-12-10 18:04:32.261149

"""

# revision identifiers, used by Alembic.
revision = '48bbb2fd01d4'
down_revision = '4223247fce24'

from alembic import op


def upgrade():
    op.drop_constraint('fk_content_revision_parent_id', 'content_revision', type_='foreignkey')
    op.create_foreign_key('content_revision_parent_id_fkey', 'content_revision', 'revisions', ['parent_id'], ['id'])


def downgrade():
    op.drop_constraint('content_revision_parent_id_fkey', 'content_revision', type_='foreignkey')
    op.create_foreign_key('fk_content_revision_parent_id', 'content_revision', 'revisions', ['parent_id'], ['id'])
