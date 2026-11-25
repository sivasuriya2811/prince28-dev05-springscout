"""The llm_calls table: write one row per model call, and add them up per day or model."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from springscout.db.models import LlmCall


def make_recorder(sessionmaker: async_sessionmaker):
    """The gateway calls this after every model call. It opens its own short session."""

    async def record(row: dict) -> None:
        async with sessionmaker() as session:
            session.add(LlmCall(**row))
            await session.commit()

    return record


class UsageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def today_cost_inr(self) -> float:
        """Total rupees spent today (Asia/Kolkata day boundary)."""
        local_now = func.timezone("Asia/Kolkata", func.now())
        local_created = func.timezone("Asia/Kolkata", LlmCall.created_at)
        stmt = select(func.coalesce(func.sum(LlmCall.cost_inr), 0)).where(
            func.date_trunc("day", local_created) == func.date_trunc("day", local_now)
        )
        total = await self.session.scalar(stmt)
        return round(float(total or 0), 6)

    async def by_day(self, days: int = 7) -> list[dict]:
        local = func.timezone("Asia/Kolkata", LlmCall.created_at)  # days as India sees them
        day = func.date_trunc("day", local).label("day")
        failed = func.sum(cast(LlmCall.status == "error", Integer))
        fallbacks = func.sum(cast(LlmCall.fallback_used, Integer))
        stmt = (
            select(
                day,
                func.count().label("calls"),
                failed.label("errors"),
                fallbacks.label("fallbacks"),
                func.sum(LlmCall.tokens_in).label("tokens_in"),
                func.sum(LlmCall.tokens_out).label("tokens_out"),
                func.sum(LlmCall.cost_inr).label("cost_inr"),
            )
            .where(LlmCall.created_at >= datetime.now(UTC) - timedelta(days=days))
            .group_by(day)
            .order_by(day.desc())
        )
        rows = await self.session.execute(stmt)
        return [
            {
                "day": row.day.date().isoformat(),
                "calls": row.calls,
                "errors": int(row.errors or 0),
                "fallbacks": int(row.fallbacks or 0),
                "tokens_in": int(row.tokens_in or 0),
                "tokens_out": int(row.tokens_out or 0),
                "cost_inr": round(float(row.cost_inr or 0), 4),
            }
            for row in rows
        ]

    async def by_model(self, days: int = 7) -> list[dict]:
        """Breakdown of calls, errors, fallbacks, latency, tokens, and spend per provider/model."""
        failed = func.sum(cast(LlmCall.status == "error", Integer))
        fallbacks = func.sum(cast(LlmCall.fallback_used, Integer))
        stmt = (
            select(
                LlmCall.provider,
                LlmCall.model,
                func.count().label("calls"),
                failed.label("errors"),
                fallbacks.label("fallbacks"),
                func.avg(LlmCall.latency_ms).label("avg_latency_ms"),
                func.sum(LlmCall.tokens_in).label("tokens_in"),
                func.sum(LlmCall.tokens_out).label("tokens_out"),
                func.sum(LlmCall.cost_inr).label("cost_inr"),
            )
            .where(LlmCall.created_at >= datetime.now(UTC) - timedelta(days=days))
            .group_by(LlmCall.provider, LlmCall.model)
            .order_by(func.count().desc())
        )
        rows = await self.session.execute(stmt)
        return [
            {
                "provider": row.provider,
                "model": row.model,
                "calls": row.calls,
                "errors": int(row.errors or 0),
                "fallbacks": int(row.fallbacks or 0),
                "avg_latency_ms": round(float(row.avg_latency_ms or 0), 1),
                "tokens_in": int(row.tokens_in or 0),
                "tokens_out": int(row.tokens_out or 0),
                "cost_inr": round(float(row.cost_inr or 0), 4),
            }
            for row in rows
        ]
