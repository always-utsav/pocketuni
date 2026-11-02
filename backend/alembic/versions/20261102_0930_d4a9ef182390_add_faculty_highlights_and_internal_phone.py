"""add faculty highlights and internal phone

Revision ID: d4a9ef182390
Revises: c398dfa91204
Create Date: 2026-11-02 09:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4a9ef182390'
down_revision = 'c398dfa91204'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('faculty_profiles', sa.Column('professional_highlights_json', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('faculty_profiles', sa.Column('external_links_json', sa.JSON(), nullable=False, server_default='{}'))
    op.add_column('faculty_profiles', sa.Column('phone_internal', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('faculty_profiles', 'phone_internal')
    op.drop_column('faculty_profiles', 'external_links_json')
    op.drop_column('faculty_profiles', 'professional_highlights_json')
