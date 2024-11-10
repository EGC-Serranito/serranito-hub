from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a287291577b1"
down_revision = "0068c51f3e68"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "treenode_bot",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("path", sa.String(length=512), nullable=False),
        sa.Column("single_child", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["treenode_bot.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tree_nodes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("path", sa.String(length=512), nullable=False),
        sa.Column("single_child", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["tree_nodes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # Obtiene la conexión actual y el inspector para verificar tablas existentes
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Elimina las tablas solo si existen
    if "tree_nodes" in inspector.get_table_names():
        op.drop_table("tree_nodes")
    if "treenode_bot" in inspector.get_table_names():
        op.drop_table("treenode_bot")
