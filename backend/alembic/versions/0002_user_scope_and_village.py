"""add user scope and village model

Revision ID: 0002_user_scope
Revises: 0001_auth_base
Create Date: 2026-04-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_user_scope'
down_revision = '0001_auth_base'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create villages table
    op.create_table(
        'villages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code'),
    )
    op.create_index(op.f('ix_villages_id'), 'villages', ['id'], unique=False)

    # Create user_village_access association table
    op.create_table(
        'user_village_access',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('village_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['village_id'], ['villages.id']),
        sa.PrimaryKeyConstraint('user_id', 'village_id'),
    )

    # Add village_id to users table using batch mode for SQLite
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('village_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_users_village_id', 'villages', ['village_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_village_id', type_='foreignkey')
        batch_op.drop_column('village_id')

    op.drop_table('user_village_access')
    op.drop_index(op.f('ix_villages_id'), table_name='villages')
    op.drop_table('villages')
