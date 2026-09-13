from alembic import context
from app.database import engine, Base
from app.auth.models import user  # noqa: F401
from app.models import suitability_db, revoked_token, wealth  # noqa: F401

if context.is_offline_mode():
    raise RuntimeError("A migração inicial adota tabelas existentes e requer conexão ao banco.")
else:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
