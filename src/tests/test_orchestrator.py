import pytest

from src.db import FishermanMemory
from src.models import IncomingMessage
from src.orchestrator import ProcurementOrchestrator


class StubShopify:
    async def fetch_unfulfilled_orders(self):
        return []


class StubWhatsApp:
    def __init__(self):
        self.sent = []

    async def send_message(self, to_phone: str, text: str):
        self.sent.append((to_phone, text))


@pytest.mark.asyncio
async def test_founder_no_cancels_active_fishermen(tmp_path):
    memory = FishermanMemory(str(tmp_path / "test.db"))
    whatsapp = StubWhatsApp()
    orchestrator = ProcurementOrchestrator(
        shopify=StubShopify(),
        whatsapp=whatsapp,
        memory=memory,
        founder_phone="+6500000000",
    )
    orchestrator.active_order_by_fisherman["+6511111111"] = "order-1"

    result = await orchestrator.handle_founder_message(
        IncomingMessage(from_phone="+6500000000", text="no")
    )

    assert result["status"] == "cancelled"
    assert "+6511111111" in orchestrator.cancelled_fishermen


@pytest.mark.asyncio
async def test_outbound_message_is_mirrored_to_founder(tmp_path):
    memory = FishermanMemory(str(tmp_path / "test.db"))
    whatsapp = StubWhatsApp()
    orchestrator = ProcurementOrchestrator(
        shopify=StubShopify(),
        whatsapp=whatsapp,
        memory=memory,
        founder_phone="+6500000000",
    )

    sent = await orchestrator.send_to_fisherman("+6511111111", "stock check")

    assert sent is True
    assert whatsapp.sent[0] == ("+6511111111", "stock check")
    assert whatsapp.sent[1][0] == "+6500000000"
    assert "[OUTBOUND] +6511111111: stock check" in whatsapp.sent[1][1]
