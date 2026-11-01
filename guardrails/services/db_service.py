"""All database I/O lives here. core/ never imports SQLAlchemy directly."""

from __future__ import annotations

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from guardrails.models.db_models import Base, GuardrailLog

load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://guardrails:guardrails_dev@localhost:5432/guardrails_db",
)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(engine)
    print(f"Tables created/verified at: {DATABASE_URL}")


def log_decision(
    *,
    user_query: str,
    layer: str,
    decision: str,
    tool_name: str | None = None,
    raw_model_output: str | None = None,
    parsed_payload: dict | None = None,
    reason: str | None = None,
    model_used: str | None = None,
    latency_ms: int | None = None,
    session_id: str | None = None,
) -> None:
    """Write one guardrail decision row. Never raises."""
    try:
        with SessionLocal() as session:
            row = GuardrailLog(
                user_query=user_query, layer=layer, decision=decision,
                tool_name=tool_name, raw_model_output=raw_model_output,
                parsed_payload=parsed_payload, reason=reason,
                model_used=model_used, latency_ms=latency_ms, session_id=session_id,
            )
            session.add(row)
            session.commit()
    except Exception as exc:
        print(f"[db_service] WARNING: failed to log decision: {exc}")


if __name__ == "__main__":
    init_db()