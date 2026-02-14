import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from pydantic import BaseModel

from src.config import settings
from src.db import FishermanMemory
from src.models import Fisherman, IncomingMessage
from src.orchestrator import ProcurementOrchestrator
from src.shopify import ShopifyClient
from src.whatsapp import WhatsAppClient


class WhatsAppWebhookPayload(BaseModel):
    from_phone: str
    text: str


class FishermanPayload(BaseModel):
    fisherman_id: str
    specialty: str
    reliability_score: float = 0.5


shopify_client = ShopifyClient(
    store_domain=settings.shopify_store_domain,
    access_token=settings.shopify_access_token,
    api_version=settings.shopify_api_version,
)
whatsapp_client = WhatsAppClient(
    api_url=settings.whatsapp_api_url,
    api_token=settings.whatsapp_api_token,
)
memory = FishermanMemory(settings.sqlite_path)
orchestrator = ProcurementOrchestrator(
    shopify=shopify_client,
    whatsapp=whatsapp_client,
    memory=memory,
    founder_phone=settings.founder_phone,
)


async def poll_shopify_forever() -> None:
    while True:
        try:
            await orchestrator.process_unfulfilled_orders()
        except Exception:
            # Keep poller alive and rely on external logging/monitoring.
            pass
        await asyncio.sleep(max(settings.poll_interval_seconds, 300))


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(poll_shopify_forever())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="Seamonger Autonomous Procurement", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/fishermen")
async def add_or_update_fisherman(payload: FishermanPayload) -> dict[str, str]:
    fisherman = Fisherman(
        fisherman_id=payload.fisherman_id,
        specialty=payload.specialty,
        reliability_score=payload.reliability_score,
    )
    memory.upsert_fisherman(fisherman)
    orchestrator.register_fisherman(payload.specialty, payload.fisherman_id)
    return {"status": "saved"}


@app.get("/fishermen")
async def list_fishermen() -> list[dict[str, str | float]]:
    fishermen = memory.list_fishermen()
    return [
        {
            "fisherman_id": f.fisherman_id,
            "specialty": f.specialty,
            "reliability_score": f.reliability_score,
        }
        for f in fishermen
    ]


@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(payload: WhatsAppWebhookPayload) -> dict:
    incoming = IncomingMessage(from_phone=payload.from_phone, text=payload.text)

    if settings.founder_phone and payload.from_phone == settings.founder_phone:
        return await orchestrator.handle_founder_message(incoming)
    return await orchestrator.handle_fisherman_message(incoming)


@app.post("/poll-now")
async def poll_now() -> dict[str, int]:
    return await orchestrator.process_unfulfilled_orders()
