import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.responses import HTMLResponse
from app.models import TicketInput, TicketResult, BatchStatus
from app.runner import run_batch, BATCHES, TICKETS

app = FastAPI(title="Support Triage API")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if not html_path.exists():
        return "<h1>Dashboard UI not found. Please check frontend/index.html</h1>"
    return html_path.read_text(encoding="utf-8")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/batches", response_model=dict)
async def create_batch(tickets: List[TicketInput], background_tasks: BackgroundTasks):
    if len(tickets) > 200:
        raise HTTPException(
            status_code=400, detail="Batch size limited to 200 tickets.")
    if len(tickets) == 0:
        raise HTTPException(status_code=400, detail="Batch cannot be empty.")

    batch_id = str(uuid.uuid4())
    background_tasks.add_task(run_batch, batch_id, tickets)
    return {"batch_id": batch_id}


@app.get("/batches/{batch_id}", response_model=BatchStatus)
async def get_batch_status(batch_id: str):
    if batch_id not in BATCHES:
        raise HTTPException(status_code=404, detail="Batch not found")
    return BATCHES[batch_id]


@app.get("/batches/{batch_id}/tickets", response_model=List[TicketResult])
async def get_batch_tickets(
    batch_id: str,
    category: Optional[str] = Query(None, description="Filter by category")
):
    if batch_id not in TICKETS:
        raise HTTPException(status_code=404, detail="Batch not found")

    results = TICKETS[batch_id]
    if category and category != "All":
        results = [t for t in results if t.category.lower() ==
                   category.lower()]

    return sorted(results, key=lambda x: (x.urgency, x.confidence), reverse=True)


@app.get("/tickets/{ticket_id}", response_model=TicketResult)
async def get_ticket(ticket_id: str):
    for ticket_list in TICKETS.values():
        for ticket in ticket_list:
            if ticket.id == ticket_id:
                return ticket
    raise HTTPException(status_code=404, detail="Ticket not found")
