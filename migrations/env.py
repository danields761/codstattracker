from alembic import context
from sqlalchemy import engine_from_config, pool

from codstattracker.storage.sql.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # target DB type from command line args
    try:
        db_type = context.get_x_argument(as_dictionary=True)['db-type']
    except KeyError:
        raise Exception(
            'Argument "-x db-type ..." is required for offline migrations!'
        )

    context.configure(
        dialect_name=db_type,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # target DB URI from command line args
    try:
        uri = context.get_x_argument(as_dictionary=True)['uri']
    except KeyError:
        raise Exception(
            'Argument "-x uri ..." is required for online migrations!'
        )

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        url=uri,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
