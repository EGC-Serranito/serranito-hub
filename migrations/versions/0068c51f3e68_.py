from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "0068c51f3e68"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    # Obtiene la conexión actual y el inspector para verificar tablas existentes
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if "treenode_bot" in inspector.get_table_names():
        op.drop_table("treenode_bot")
    if "tree_nodes" in inspector.get_table_names():
        op.drop_table("tree_nodes")


def downgrade():
    # Re-crea las tablas en caso de un downgrade
    op.create_table(
        "tree_nodes",
        sa.Column(
            "id", mysql.INTEGER(display_width=11), autoincrement=True, nullable=False
        ),
        sa.Column(
            "user_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("name", mysql.VARCHAR(length=256), nullable=False),
        sa.Column(
            "parent_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("path", mysql.VARCHAR(length=512), nullable=False),
        sa.Column(
            "single_child",
            mysql.TINYINT(display_width=1),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["tree_nodes.id"],
            name="tree_nodes_ibfk_1",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name="tree_nodes_ibfk_2"),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_general_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_table(
        "treenode_bot",
        sa.Column(
            "id", mysql.INTEGER(display_width=11), autoincrement=True, nullable=False
        ),
        sa.Column("name", mysql.VARCHAR(length=256), nullable=False),
        sa.Column(
            "parent_id",
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("path", mysql.VARCHAR(length=512), nullable=False),
        sa.Column(
            "single_child",
            mysql.TINYINT(display_width=1),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["treenode_bot.id"],
            name="treenode_bot_ibfk_1",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_general_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
