"""Primeira migração

Revision ID: 4bd74897acbb
Revises: 
Create Date: 2025-04-20 14:36:27.795181

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bd74897acbb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "pacientes",  # Keep the table name in Portuguese, as the data is in Portuguese
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String),
        sa.Column("attendance_day", sa.Enum("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY", name="weekdays")),
        sa.Column("time", sa.String),
        sa.Column("health_plan", sa.String, nullable=True),
        sa.Column("clinic_value", sa.Float),
        sa.Column("therapist_percentage", sa.Float),
    )
    op.create_table(
        "atendimentos",  # Keep the table name in Portuguese
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("date", sa.Date),
        sa.Column("patient_id", sa.Integer, sa.ForeignKey("pacientes.id")),
        sa.Column("record_done", sa.Boolean, default=False),
        sa.Column("record_launched", sa.Boolean, default=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("atendimentos")
    op.drop_table("pacientes")
