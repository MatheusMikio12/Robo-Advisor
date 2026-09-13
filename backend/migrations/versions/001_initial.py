"""Schema inicial, incluindo adoção não destrutiva de bancos anteriores ao Alembic."""
from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    existing = set(sa.inspect(op.get_bind()).get_table_names())
    if "users" not in existing:
        op.create_table("users", sa.Column("id", sa.Integer, primary_key=True), sa.Column("email", sa.String, nullable=False),
                        sa.Column("hashed_password", sa.String, nullable=False), sa.Column("is_active", sa.Boolean))
        op.create_index("ix_users_id", "users", ["id"])
        op.create_index("ix_users_email", "users", ["email"], unique=True)
    if "perfis" not in existing:
        op.create_table("perfis", sa.Column("id", sa.Integer, primary_key=True),
                        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
                        sa.Column("perfil_classificado", sa.String, nullable=False), sa.Column("idade", sa.Integer, nullable=False),
                        sa.Column("renda", sa.Float, nullable=False), sa.Column("patrimonio", sa.Float, nullable=False),
                        sa.Column("horizonte_anos", sa.Integer, nullable=False), sa.Column("objetivo", sa.String, nullable=False),
                        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
        op.create_index("ix_perfis_id", "perfis", ["id"])
        op.create_index("ix_perfis_user_id", "perfis", ["user_id"], unique=True)
    if "revoked_tokens" not in existing:
        op.create_table("revoked_tokens", sa.Column("id", sa.Integer, primary_key=True), sa.Column("jti", sa.String, nullable=False),
                        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
                        sa.Column("revoked_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
        op.create_index("ix_revoked_tokens_id", "revoked_tokens", ["id"])
        op.create_index("ix_revoked_tokens_jti", "revoked_tokens", ["jti"], unique=True)
    if "financial_profiles" not in existing:
        op.create_table("financial_profiles", sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
                        sa.Column("data", sa.JSON, nullable=False), sa.Column("revision", sa.Integer, nullable=False),
                        sa.Column("updated_at", sa.DateTime(timezone=True)))
    if "wealth_records" not in existing:
        op.create_table("wealth_records", sa.Column("id", sa.String(36), primary_key=True),
                        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
                        sa.Column("kind", sa.String(30), nullable=False), sa.Column("external_id", sa.String(100)),
                        sa.Column("data", sa.JSON, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True)),
                        sa.Column("updated_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("user_id", "kind", "external_id"))
        op.create_index("ix_wealth_records_user_id", "wealth_records", ["user_id"])
        op.create_index("ix_wealth_records_kind", "wealth_records", ["kind"])
    if "products" not in existing:
        op.create_table("products", sa.Column("id", sa.String(120), primary_key=True), sa.Column("data", sa.JSON, nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True)))
    if "audit_events" not in existing:
        op.create_table("audit_events", sa.Column("id", sa.String(36), primary_key=True),
                        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
                        sa.Column("action", sa.String(80), nullable=False), sa.Column("data", sa.JSON, nullable=False),
                        sa.Column("created_at", sa.DateTime(timezone=True)))
        op.create_index("ix_audit_events_user_id", "audit_events", ["user_id"])


def downgrade():
    raise RuntimeError("Esta migração pode adotar tabelas preexistentes. Restaure um backup para reverter sem apagar dados do usuário.")
