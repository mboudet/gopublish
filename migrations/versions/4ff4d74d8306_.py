"""empty message

Revision ID: 4ff4d74d8306
Revises: a74da9a0ce76
Create Date: 2022-01-28 19:10:00.129795

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4ff4d74d8306'
down_revision = 'a74da9a0ce76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_tag_tag'), 'tag', ['tag'], unique=False)
    op.create_table('file_tag',
    sa.Column('file_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['published_file.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('file_id', 'tag_id')
    )
    op.create_unique_constraint(None, 'published_file', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'published_file', type_='unique')
    op.drop_table('file_tag')
    op.drop_index(op.f('ix_tag_tag'), table_name='tag')
    op.drop_table('tag')
    # ### end Alembic commands ###
