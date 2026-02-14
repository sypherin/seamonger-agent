from copy import deepcopy

import pytest

from src.db import FishermanMemory
from src.models import Fisherman, IncomingMessage
from src.orchestrator import ProcurementOrchestrator
from tests.mock_data import FISHERMEN, FOUNDER_PHONE, SINGLISH_REPLY, UNFULFILLED_ORDERS


class StubShopify:
    async def fetch_unfulfilled_orders(self):
        return deepcopy(UNFULFILLED_ORDERS)


class StubWhatsApp:
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    async def send_message(self, to_phone: str, text: str):
        self.sent.append((to_phone, text))


@pytest.mark.asyncio
async def test_full_procurement_simulation_end_to_end(tmp_path):
    memory = FishermanMemory(str(tmp_path / "simulation.db"))
    whatsapp = StubWhatsApp()
    orchestrator = ProcurementOrchestrator(
        shopify=StubShopify(),
        whatsapp=whatsapp,
        memory=memory,
        founder_phone=FOUNDER_PHONE,
    )

    for row in FISHERMEN:
        fisherman = Fisherman(**row)
        memory.upsert_fisherman(fisherman)
        orchestrator.register_fisherman(fisherman.specialty, fisherman.fisherman_id)

    poll_result = await orchestrator.process_unfulfilled_orders()
    print("SIM_STEP 1 Shopify order detection:", poll_result)

    assert poll_result["orders"] == 1
    assert poll_result["messages_sent"] == 1

    selected_fisherman = FISHERMEN[0]["fisherman_id"]
    assert whatsapp.sent[0][0] == selected_fisherman
    assert "Fresh Snapper Fillet" in whatsapp.sent[0][1]
    print("SIM_STEP 2 Fisherman selected:", selected_fisherman)

    assert whatsapp.sent[1][0] == FOUNDER_PHONE
    assert "[OUTBOUND]" in whatsapp.sent[1][1]
    assert selected_fisherman in whatsapp.sent[1][1]
    print("SIM_STEP 3 Founder outbound mirror:", whatsapp.sent[1][1])

    inbound = IncomingMessage(from_phone=selected_fisherman, text=SINGLISH_REPLY)
    inbound_result = await orchestrator.handle_fisherman_message(inbound)
    print("SIM_STEP 4 Singlish parse + processing:", inbound_result)

    assert inbound_result["status"] == "processed"
    assert inbound_result["signal"]["product"] == "snapper"
    assert inbound_result["signal"]["quantity_kg"] == 50.0

    updated_fisherman = memory.get_fisherman(selected_fisherman)
    assert updated_fisherman is not None
    assert updated_fisherman.reliability_score == pytest.approx(0.97)
    print("SIM_STEP 5 DB reliability update:", updated_fisherman.reliability_score)

    assert whatsapp.sent[2][0] == FOUNDER_PHONE
    assert "[INBOUND]" in whatsapp.sent[2][1]
    assert SINGLISH_REPLY in whatsapp.sent[2][1]
    print("SIM_STEP 6 Founder inbound mirror:", whatsapp.sent[2][1])
