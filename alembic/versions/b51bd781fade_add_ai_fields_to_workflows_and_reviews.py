"""add_ai_fields_to_workflows_and_reviews

Revision ID: b51bd781fade
Revises: 87c87c6b196a
Create Date: 2026-01-21 00:04:57.328704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b51bd781fade'
down_revision: Union[str, Sequence[str], None] = '87c87c6b196a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add AI fields to workflows and code_reviews tables."""
    
    # Add AI fields to workflows table
    op.add_column('workflows', sa.Column('ai_summary', sa.Text(), nullable=True))
    op.add_column('workflows', sa.Column('ai_recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Add AI fields to code_reviews table
    op.add_column('code_reviews', sa.Column('ai_issues', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('code_reviews', sa.Column('ai_best_practices', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('code_reviews', sa.Column('ai_security_concerns', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('code_reviews', sa.Column('ai_refactoring_suggestions', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    """Downgrade schema - Remove AI fields from workflows and code_reviews tables."""
    
    # Remove AI fields from code_reviews table
    op.drop_column('code_reviews', 'ai_refactoring_suggestions')
    op.drop_column('code_reviews', 'ai_security_concerns')
    op.drop_column('code_reviews', 'ai_best_practices')
    op.drop_column('code_reviews', 'ai_issues')
    
    # Remove AI fields from workflows table
    op.drop_column('workflows', 'ai_recommendations')
    op.drop_column('workflows', 'ai_summary')
