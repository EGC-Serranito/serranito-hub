"""
first migration

Revision ID: 001
Revises:
Create Date: 2024-09-08 16:50:20.326640
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'doi_mapping',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dataset_doi_old', sa.String(length=120), nullable=True),
        sa.Column('dataset_doi_new', sa.String(length=120), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'ds_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number_of_models', sa.String(length=120), nullable=True),
        sa.Column('number_of_features', sa.String(length=120), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'fm_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solver', sa.Text(), nullable=True),
        sa.Column('not_solver', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=256), nullable=False),
        sa.Column('password', sa.String(length=256), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_table(
        'webhook',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'zenodo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'ds_meta_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('deposition_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column(
            'publication_type',
            sa.Enum(
                'NONE', 'ANNOTATION_COLLECTION', 'BOOK', 'BOOK_SECTION',
                'CONFERENCE_PAPER', 'DATA_MANAGEMENT_PLAN', 'JOURNAL_ARTICLE',
                'PATENT', 'PREPRINT', 'PROJECT_DELIVERABLE',
                'PROJECT_MILESTONE', 'PROPOSAL', 'REPORT',
                'SOFTWARE_DOCUMENTATION', 'TAXONOMIC_TREATMENT',
                'TECHNICAL_NOTE', 'THESIS', 'WORKING_PAPER', 'OTHER',
                name='publicationtype'
            ),
            nullable=False
        ),
        sa.Column('publication_doi', sa.String(length=120), nullable=True),
        sa.Column('dataset_doi', sa.String(length=120), nullable=True),
        sa.Column('tags', sa.String(length=120), nullable=True),
        sa.Column('ds_metrics_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['ds_metrics_id'], ['ds_metrics.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'fm_meta_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uvl_filename', sa.String(length=120), nullable=False),
        sa.Column('title', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column(
            'publication_type',
            sa.Enum(
                'NONE', 'ANNOTATION_COLLECTION', 'BOOK', 'BOOK_SECTION',
                'CONFERENCE_PAPER', 'DATA_MANAGEMENT_PLAN', 'JOURNAL_ARTICLE',
                'PATENT', 'PREPRINT', 'PROJECT_DELIVERABLE',
                'PROJECT_MILESTONE', 'PROPOSAL', 'REPORT',
                'SOFTWARE_DOCUMENTATION', 'TAXONOMIC_TREATMENT',
                'TECHNICAL_NOTE', 'THESIS', 'WORKING_PAPER', 'OTHER',
                name='publicationtype'
            ),
            nullable=False
        ),
        sa.Column('publication_doi', sa.String(length=120), nullable=True),
        sa.Column('tags', sa.String(length=120), nullable=True),
        sa.Column('uvl_version', sa.String(length=120), nullable=True),
        sa.Column('fm_metrics_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['fm_metrics_id'], ['fm_metrics.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'user_profile',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('orcid', sa.String(length=19), nullable=True),
        sa.Column('affiliation', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('surname', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_table(
        'author',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('affiliation', sa.String(length=120), nullable=True),
        sa.Column('orcid', sa.String(length=120), nullable=True),
        sa.Column('ds_meta_data_id', sa.Integer(), nullable=True),
        sa.Column('fm_meta_data_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['ds_meta_data_id'], ['ds_meta_data.id']),
        sa.ForeignKeyConstraint(['fm_meta_data_id'], ['fm_meta_data.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'data_set',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ds_meta_data_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ds_meta_data_id'], ['ds_meta_data.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'ds_download_record',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('dataset_id', sa.Integer(), nullable=True),
        sa.Column('download_date', sa.DateTime(), nullable=False),
        sa.Column('download_cookie', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['dataset_id'], ['data_set.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'ds_view_record',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('dataset_id', sa.Integer(), nullable=True),
        sa.Column('view_date', sa.DateTime(), nullable=False),
        sa.Column('view_cookie', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['dataset_id'], ['data_set.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'tree_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('path', sa.String(512), nullable=False),
        sa.Column('single_child', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['tree_nodes.id'],
                                ondelete="CASCADE"),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'treenode_bot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('path', sa.String(512), nullable=False),
        sa.Column('single_child', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['parent_id'], ['treenode_bot.id'],
                                ondelete="CASCADE"),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('treenode_bot')
    op.drop_table('tree_nodes')
    op.drop_table('ds_view_record')
    op.drop_table('ds_download_record')
    op.drop_table('data_set')
    op.drop_table('author')
    op.drop_table('user_profile')
    op.drop_table('fm_meta_data')
    op.drop_table('ds_meta_data')
    op.drop_table('zenodo')
    op.drop_table('webhook')
    op.drop_table('user')
    op.drop_table('fm_metrics')
    op.drop_table('ds_metrics')
    op.drop_table('doi_mapping')
