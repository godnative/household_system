"""add household and member models

Revision ID: 0003_household_member
Revises: 0002_user_scope
Create Date: 2026-04-23

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0003_household_member'
down_revision = '0002_user_scope'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create households table
    op.create_table(
        'households',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('village_id', sa.Integer(), nullable=False),
        sa.Column('plot_number', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(length=200), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('head_of_household', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['village_id'], ['villages.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_households_id'), 'households', ['id'], unique=False)
    op.create_index(op.f('ix_households_village_id'), 'households', ['village_id'], unique=False)

    # Create members table
    op.create_table(
        'members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('household_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('gender', sa.String(length=10), nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('baptismal_name', sa.String(length=50), nullable=True),
        sa.Column('relation_to_head', sa.String(length=20), nullable=True),
        sa.Column('education', sa.String(length=50), nullable=True),
        sa.Column('move_in_date', sa.Date(), nullable=True),
        sa.Column('occupation', sa.String(length=100), nullable=True),
        sa.Column('church_id', sa.String(length=50), nullable=True),
        # 圣洗
        sa.Column('baptism_priest', sa.String(length=50), nullable=True),
        sa.Column('baptism_godparent', sa.String(length=50), nullable=True),
        sa.Column('baptism_date', sa.Date(), nullable=True),
        sa.Column('baptism_note', sa.Text(), nullable=True),
        # 初领圣体
        sa.Column('first_communion_date', sa.Date(), nullable=True),
        # 补礼
        sa.Column('supplementary_priest', sa.String(length=50), nullable=True),
        sa.Column('supplementary_place', sa.String(length=100), nullable=True),
        sa.Column('supplementary_date', sa.Date(), nullable=True),
        # 照片
        sa.Column('photo', sa.String(length=255), nullable=True),
        # 坚振
        sa.Column('confirmation_date', sa.Date(), nullable=True),
        sa.Column('confirmation_priest', sa.String(length=50), nullable=True),
        sa.Column('confirmation_godparent', sa.String(length=50), nullable=True),
        sa.Column('confirmation_name', sa.String(length=50), nullable=True),
        sa.Column('confirmation_age', sa.Integer(), nullable=True),
        sa.Column('confirmation_place', sa.String(length=100), nullable=True),
        # 婚配
        sa.Column('marriage_date', sa.Date(), nullable=True),
        sa.Column('marriage_priest', sa.String(length=50), nullable=True),
        sa.Column('marriage_witness', sa.String(length=100), nullable=True),
        sa.Column('marriage_dispensation_item', sa.String(length=100), nullable=True),
        sa.Column('marriage_dispensation_priest', sa.String(length=50), nullable=True),
        sa.Column('marriage_place', sa.String(length=100), nullable=True),
        # 病人傅油
        sa.Column('anointing_date', sa.Date(), nullable=True),
        sa.Column('anointing_priest', sa.String(length=50), nullable=True),
        sa.Column('anointing_place', sa.String(length=100), nullable=True),
        # 死亡
        sa.Column('death_date', sa.Date(), nullable=True),
        sa.Column('death_age', sa.Integer(), nullable=True),
        # 善会
        sa.Column('association', sa.String(length=100), nullable=True),
        # 备注
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['household_id'], ['households.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_members_id'), 'members', ['id'], unique=False)
    op.create_index(op.f('ix_members_household_id'), 'members', ['household_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_members_household_id'), table_name='members')
    op.drop_index(op.f('ix_members_id'), table_name='members')
    op.drop_table('members')

    op.drop_index(op.f('ix_households_village_id'), table_name='households')
    op.drop_index(op.f('ix_households_id'), table_name='households')
    op.drop_table('households')
