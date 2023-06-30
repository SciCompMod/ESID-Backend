"""init tables

Revision ID: 28b8f1e29116
Revises: 
Create Date: 2022-12-20 09:27:08.386991

"""
import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28b8f1e29116'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('aggregation',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('compartment',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('tags', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('compartmentaggregation',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('tags', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('group',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('intervention',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('model',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('node',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('ags', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('nodelist',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parameterdefinition',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tag',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('aggregationtaglink',
    sa.Column('tag_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('aggregation_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['aggregation_id'], ['aggregation.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('tag_id', 'aggregation_id')
    )
    op.create_table('modelaggregationlink',
    sa.Column('model_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('aggregation_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['aggregation_id'], ['aggregation.id'], ),
    sa.ForeignKeyConstraint(['model_id'], ['model.id'], ),
    sa.PrimaryKeyConstraint('model_id', 'aggregation_id')
    )
    op.create_table('modelcompartmentlink',
    sa.Column('compartment_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('model_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['compartment_name'], ['compartment.name'], ),
    sa.ForeignKeyConstraint(['model_id'], ['model.id'], ),
    sa.PrimaryKeyConstraint('compartment_name', 'model_id')
    )
    op.create_table('modelgrouplink',
    sa.Column('group_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('model_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['model_id'], ['model.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'model_id')
    )
    op.create_table('nodenodelistlink',
    sa.Column('node_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('nodelist_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['node_id'], ['node.id'], ),
    sa.ForeignKeyConstraint(['nodelist_id'], ['nodelist.id'], ),
    sa.PrimaryKeyConstraint('node_id', 'nodelist_id')
    )
    op.create_table('scenario',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('model_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('node_list_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['model_id'], ['model.id'], ),
    sa.ForeignKeyConstraint(['node_list_id'], ['nodelist.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('scenariointerventionlink',
    sa.Column('scenario_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('intervention_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['intervention_id'], ['intervention.id'], ),
    sa.ForeignKeyConstraint(['scenario_id'], ['scenario.id'], ),
    sa.PrimaryKeyConstraint('scenario_id', 'intervention_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('scenariointerventionlink')
    op.drop_table('scenario')
    op.drop_table('nodenodelistlink')
    op.drop_table('modelgrouplink')
    op.drop_table('modelcompartmentlink')
    op.drop_table('modelaggregationlink')
    op.drop_table('aggregationtaglink')
    op.drop_table('tag')
    op.drop_table('parameterdefinition')
    op.drop_table('nodelist')
    op.drop_table('node')
    op.drop_table('model')
    op.drop_table('intervention')
    op.drop_table('group')
    op.drop_table('compartmentaggregation')
    op.drop_table('compartment')
    op.drop_table('aggregation')
    # ### end Alembic commands ###
