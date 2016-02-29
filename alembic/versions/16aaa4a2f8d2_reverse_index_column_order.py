"""Reverse index column order

Revision ID: 16aaa4a2f8d2
Revises: 48bbb2fd01d4
Create Date: 2016-02-29 12:43:23.244272

"""

# revision identifiers, used by Alembic.
revision = '16aaa4a2f8d2'
down_revision = '48bbb2fd01d4'

from alembic import op
# import sqlalchemy as sa


def upgrade():
    op.drop_constraint('folder_name_website_id_key', 'folder', type_='unique')
    op.create_unique_constraint('folder_website_id_name_key', 'folder', ['website_id', 'name'])
    op.drop_constraint('node_name_folder_id_key', 'node', type_='unique')
    op.create_unique_constraint('node_folder_id_name_key', 'node', ['folder_id', 'name'])
    op.drop_constraint('property_name_node_id_key', 'property', type_='unique')
    op.create_unique_constraint('property_node_id_name_key', 'property', ['node_id', 'name'])


def downgrade():
    op.drop_constraint('property_node_id_name_key', 'property', type_='unique')
    op.create_unique_constraint('property_name_node_id_key', 'property', ['name', 'node_id'])
    op.drop_constraint('node_folder_id_name_key', 'node', type_='unique')
    op.create_unique_constraint('node_name_folder_id_key', 'node', ['name', 'folder_id'])
    op.drop_constraint('folder_website_id_name_key', 'folder', type_='unique')
    op.create_unique_constraint('folder_name_website_id_key', 'folder', ['name', 'website_id'])
