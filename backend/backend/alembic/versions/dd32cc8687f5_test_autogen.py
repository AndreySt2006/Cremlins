"""
Test autogen
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd32cc8687f5'
down_revision: Union[str, Sequence[str], None] = 'da311443c8b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # No-op downgrade: creation of spatial_ref_sys is managed by PostGIS.
    pass
    # ### end Alembic commands ###
