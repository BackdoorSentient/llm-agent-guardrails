"""SQLAlchemy table definitions. No connection logic here — see services/db_service.py."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    String, Text, Boolean, Integer, BigInteger, DateTime, JSON,
    CheckConstraint, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class GuardrailLog(Base):
    __tablename__ = "guardrail_logs"
    __table_args__ = (
        CheckConstraint("layer IN ('schema','allowlist','override')", name="ck_layer"),
        CheckConstraint("decision IN ('passed','blocked','overridden','fallback')", name="ck_decision"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc))
    session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    layer: Mapped[str] = mapped_column(String, nullable=False)
    decision: Mapped[str] = mapped_column(String, nullable=False)
    tool_name: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_model_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)


class AllowlistConfig(Base):
    __tablename__ = "allowlist_config"
    __table_args__ = (UniqueConstraint("tool_name", name="uq_tool_name"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tool_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc))
    added_by: Mapped[str] = mapped_column(String, default="system")


class EvalResult(Base):
    __tablename__ = "eval_results"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc))
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    expected_outcome: Mapped[str] = mapped_column(String, nullable=False)
    actual_outcome: Mapped[str] = mapped_column(String, nullable=False)
    caught: Mapped[bool] = mapped_column(Boolean, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String, nullable=True)
    judge_model: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)