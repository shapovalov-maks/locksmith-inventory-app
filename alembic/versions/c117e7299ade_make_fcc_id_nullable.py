from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c117e7299ade'
down_revision = 'd9f854851d2a'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('keys', 'fcc_id',
               existing_type=sa.String(),
               nullable=True)

def downgrade():
    op.alter_column('keys', 'fcc_id',
               existing_type=sa.String(),
               nullable=False)
