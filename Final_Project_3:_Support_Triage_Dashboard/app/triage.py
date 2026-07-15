import asyncio
from app.models import TicketInput, TicketResult
from app.ai import classify_ticket_api


async def triage_ticket(ticket: TicketInput, sem: asyncio.Semaphore) -> TicketResult:
    async with sem:
        try:
            return await classify_ticket_api(ticket)
        except Exception as e:
            # Isolation d'erreur : évite de faire planter tout le batch
            return TicketResult(
                id=ticket.id,
                category="Error",
                urgency=1,
                sentiment="neutral",
                draft_reply="Erreur lors du traitement.",
                confidence=0.0,
                error=str(e)
            )
