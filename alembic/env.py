import importlib
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

import os
import sys
sys.path.insert(0, os.path.realpath("."))

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

from libs.db.dbsession import Base

from Setting import INSTALLED_MODELS

for models in INSTALLED_MODELS:
    try:
        importlib.import_module(models)  # 根据ADMIN_INSTALLED_APPS导入app模块
    except ModuleNotFoundError as e:
        raise ImportError('no model name {}'.format(models))

target_metadata = Base.metadata

"""

首先创建一个基本数据库版本，你当然可以从已有的数据库出发。
alembic revision -m "create account table"
然后就可以进行数据库的修改然后生成新的数据库迁移文件
再进行迁移数据库就不会出现问题（讲已经生成的数据表删除并且无法重建）
alembic revision --autogenerate -m "first commit"
alembic upgrade head

"""

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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
