"""Initial migration.

Revision ID: 925a2c465d4f
Revises: 
Create Date: 2021-02-25 14:50:28.149337

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '925a2c465d4f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('published_file',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('task_id', sa.String(length=255), nullable=True),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('file_path', sa.String(length=255), nullable=False),
    sa.Column('old_file_path', sa.String(length=255), nullable=False),
    sa.Column('repo_path', sa.String(length=255), nullable=False),
    sa.Column('hash', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=255), nullable=False),
    sa.Column('publishing_date', sa.DateTime(), nullable=False),
    sa.Column('size', sa.BigInteger(), nullable=False),
    sa.Column('owner', sa.String(length=255), nullable=False),
    sa.Column('contact', sa.String(length=255), nullable=True),
    sa.Column('error', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_published_file_contact'), 'published_file', ['contact'], unique=False)
    op.create_index(op.f('ix_published_file_file_name'), 'published_file', ['file_name'], unique=False)
    op.create_index(op.f('ix_published_file_file_path'), 'published_file', ['file_path'], unique=False)
    op.create_index(op.f('ix_published_file_hash'), 'published_file', ['hash'], unique=False)
    op.create_index(op.f('ix_published_file_old_file_path'), 'published_file', ['old_file_path'], unique=False)
    op.create_index(op.f('ix_published_file_owner'), 'published_file', ['owner'], unique=False)
    op.create_index(op.f('ix_published_file_repo_path'), 'published_file', ['repo_path'], unique=False)
    op.create_index(op.f('ix_published_file_size'), 'published_file', ['size'], unique=False)
    op.create_index(op.f('ix_published_file_task_id'), 'published_file', ['task_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_published_file_task_id'), table_name='published_file')
    op.drop_index(op.f('ix_published_file_size'), table_name='published_file')
    op.drop_index(op.f('ix_published_file_repo_path'), table_name='published_file')
    op.drop_index(op.f('ix_published_file_owner'), table_name='published_file')
    op.drop_index(op.f('ix_published_file_old_file_path'), table_name='published_file')
    op.drop_index(op.f('ix_published_file_hash'), table_name='published_file')
    op.drop_index(op.f('ix_published_file_file_path'), table_name='published_file')
    op.drop_index(op.f('ix_published_file_file_name'), table_name='published_file')
    op.drop_index(op.f('ix_published_file_contact'), table_name='published_file')
    op.drop_table('published_file')
    # ### end Alembic commands ###
