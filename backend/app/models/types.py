from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

# JSONB en PostgreSQL, JSON en SQLite
JsonType = JSON().with_variant(JSONB(), "postgresql")
