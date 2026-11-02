"""Add academic intelligence and application outbox tables

Revision ID: c398dfa91204
Revises: f45e46a94da4
Create Date: 2026-11-02 02:00:00.000000+00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c398dfa91204'
down_revision: Union[str, None] = 'f45e46a94da4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. laboratories
    op.create_table(
        'laboratories',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_demo', sa.Boolean(), default=False, nullable=False),
        sa.Column('data_source', sa.String(length=50), default='official', nullable=False),
        sa.Column('department_id', sa.String(length=36), sa.ForeignKey('departments.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('name', sa.String(length=255), nullable=False, index=True),
        sa.Column('code', sa.String(length=50), nullable=True, index=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('capacity', sa.Integer(), default=30, nullable=False),
        sa.Column('hardware_specs', sa.Text(), nullable=True),
        sa.Column('software_specs', sa.Text(), nullable=True),
        sa.Column('faculty_in_charge', sa.String(length=255), nullable=True),
        sa.Column('staff_in_charge', sa.String(length=255), nullable=True),
        sa.Column('research_focus', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
    )

    # 2. department_programmes
    op.create_table(
        'department_programmes',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_demo', sa.Boolean(), default=False, nullable=False),
        sa.Column('data_source', sa.String(length=50), default='official', nullable=False),
        sa.Column('department_id', sa.String(length=36), sa.ForeignKey('departments.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('name', sa.String(length=255), nullable=False, index=True),
        sa.Column('degree', sa.String(length=50), nullable=False),
        sa.Column('intake', sa.Integer(), default=60, nullable=False),
        sa.Column('duration_years', sa.Integer(), default=4, nullable=False),
        sa.Column('curriculum_url', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
    )

    # 3. bos_members
    op.create_table(
        'bos_members',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_demo', sa.Boolean(), default=False, nullable=False),
        sa.Column('data_source', sa.String(length=50), default='official', nullable=False),
        sa.Column('department_id', sa.String(length=36), sa.ForeignKey('departments.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('name', sa.String(length=255), nullable=False, index=True),
        sa.Column('designation', sa.String(length=255), nullable=True),
        sa.Column('affiliation', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
    )

    # 4. department_events
    op.create_table(
        'department_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_demo', sa.Boolean(), default=False, nullable=False),
        sa.Column('data_source', sa.String(length=50), default='official', nullable=False),
        sa.Column('department_id', sa.String(length=36), sa.ForeignKey('departments.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('title', sa.String(length=255), nullable=False, index=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('date_start', sa.String(length=50), nullable=True),
        sa.Column('date_end', sa.String(length=50), nullable=True),
        sa.Column('coordinator', sa.String(length=255), nullable=True),
        sa.Column('speaker', sa.String(length=255), nullable=True),
        sa.Column('brochure_url', sa.String(length=500), nullable=True),
        sa.Column('report_url', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
    )

    # 5. class_coordinators
    op.create_table(
        'class_coordinators',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_demo', sa.Boolean(), default=False, nullable=False),
        sa.Column('data_source', sa.String(length=50), default='official', nullable=False),
        sa.Column('year', sa.String(length=50), nullable=False, index=True),
        sa.Column('branch', sa.String(length=100), nullable=False, index=True),
        sa.Column('faculty_name', sa.String(length=255), nullable=False, index=True),
        sa.Column('contact_number', sa.String(length=50), nullable=True),
        sa.Column('institutional_email', sa.String(length=255), nullable=True),
        sa.Column('academic_session', sa.String(length=50), default='2026-2027', nullable=False),
    )

    # 6. conflict_reviews
    op.create_table(
        'conflict_reviews',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_demo', sa.Boolean(), default=False, nullable=False),
        sa.Column('data_source', sa.String(length=50), default='official', nullable=False),
        sa.Column('source_document', sa.String(length=255), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('source_content', sa.Text(), nullable=False),
        sa.Column('conflict_description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), default='PENDING', nullable=False),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
    )

    # 7. application_outbox
    op.create_table(
        'application_outbox',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_demo', sa.Boolean(), default=False, nullable=False),
        sa.Column('data_source', sa.String(length=50), default='official', nullable=False),
        sa.Column('application_id', sa.String(length=36), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('recipient_email', sa.String(length=255), nullable=False),
        sa.Column('recipient_name', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), default='QUEUED', nullable=False, index=True),
        sa.Column('provider_response', sa.Text(), nullable=True),
        sa.Column('attempt_count', sa.Integer(), default=0, nullable=False),
        sa.Column('dispatched_at', sa.DateTime(timezone=True), nullable=True),
    )

    # 8. timetable_entries columns
    op.add_column('timetable_entries', sa.Column('section', sa.String(length=20), nullable=True, server_default='A'))
    op.add_column('timetable_entries', sa.Column('batch_group', sa.String(length=20), nullable=True, server_default='All'))
    op.add_column('timetable_entries', sa.Column('slot_number', sa.Integer(), nullable=True))
    op.add_column('timetable_entries', sa.Column('is_lab', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('timetable_entries', 'is_lab')
    op.drop_column('timetable_entries', 'slot_number')
    op.drop_column('timetable_entries', 'batch_group')
    op.drop_column('timetable_entries', 'section')
    op.drop_table('application_outbox')
    op.drop_table('conflict_reviews')
    op.drop_table('class_coordinators')
    op.drop_table('department_events')
    op.drop_table('bos_members')
    op.drop_table('department_programmes')
    op.drop_table('laboratories')
