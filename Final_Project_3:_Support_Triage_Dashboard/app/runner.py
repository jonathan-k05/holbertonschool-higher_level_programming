import os
import asyncio
from typing import Dict, List
from app.models import TicketInput, TicketResult, BatchStatus
from app.triage import triage_ticket

# Stockage en mémoire simple pour l'exercice
BATCHES: Dict[str, BatchStatus] = {}
TICKETS: Dict[str, List[TicketResult]] = {}


async def run_batch(batch_id: str, tickets: List[TicketInput]):
    concurrency = int(os.getenv("CONCURRENCY_LIMIT", "8"))
    sem = asyncio.Semaphore(concurrency)

    BATCHES[batch_id] = BatchStatus(
        id=batch_id,
        total=len(tickets),
        completed=0,
        failed=0,
        status="processing"
    )
    TICKETS[batch_id] = []

    tasks = [triage_ticket(t, sem) for t in tickets]

    # Exécution des tâches avec mise à jour en temps réel au fur et à mesure
    for future in asyncio.as_completed(tasks):
        result: TicketResult = await future
        TICKETS[batch_id].append(result)

        if result.error:
            BATCHES[batch_id].failed += 1
        else:
            BATCHES[batch_id].completed += 1

    BATCHES[batch_id].status = "completed"
