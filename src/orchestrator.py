from collections import defaultdict
from typing import Any

from src.db import FishermanMemory
from src.models import IncomingMessage
from src.parser import parse_stock_signal
from src.shopify import ShopifyClient
from src.whatsapp import WhatsAppClient


class ProcurementOrchestrator:
    def __init__(
        self,
        shopify: ShopifyClient,
        whatsapp: WhatsAppClient,
        memory: FishermanMemory,
        founder_phone: str,
    ) -> None:
        self.shopify = shopify
        self.whatsapp = whatsapp
        self.memory = memory
        self.founder_phone = founder_phone
        self.cancelled_fishermen: set[str] = set()
        self.active_order_by_fisherman: dict[str, str] = {}
        self.fishermen_directory: dict[str, list[str]] = defaultdict(list)

    def _select_best_fisherman(self, product_name: str) -> str | None:
        normalized_product = product_name.strip().lower()
        candidate_phones: set[str] = set()

        for specialty, fishermen in self.fishermen_directory.items():
            if specialty in normalized_product:
                candidate_phones.update(fishermen)

        if not candidate_phones:
            return None

        def score(phone: str) -> tuple[int, float]:
            fisherman = self.memory.get_fisherman(phone)
            if fisherman is None:
                return (0, 0.0)
            specialty_match = 1 if fisherman.specialty.strip().lower() in normalized_product else 0
            return (specialty_match, fisherman.reliability_score)

        return max(candidate_phones, key=score)

    def register_fisherman(self, product: str, phone: str) -> None:
        product_key = product.strip().lower()
        if phone not in self.fishermen_directory[product_key]:
            self.fishermen_directory[product_key].append(phone)

    async def mirror_to_founder(self, direction: str, phone: str, message: str) -> None:
        if not self.founder_phone:
            return
        mirror_text = f"[{direction}] {phone}: {message}"
        await self.whatsapp.send_message(self.founder_phone, mirror_text)

    async def send_to_fisherman(self, fisherman_phone: str, message: str) -> bool:
        if fisherman_phone in self.cancelled_fishermen:
            return False
        await self.whatsapp.send_message(fisherman_phone, message)
        await self.mirror_to_founder("OUTBOUND", fisherman_phone, message)
        return True

    async def handle_founder_message(self, incoming: IncomingMessage) -> dict[str, Any]:
        if incoming.text.strip().lower() == "no":
            # Founder-level emergency stop for all currently active fishermen.
            for fisherman_phone in list(self.active_order_by_fisherman.keys()):
                self.cancelled_fishermen.add(fisherman_phone)
            return {"status": "cancelled", "count": len(self.cancelled_fishermen)}
        return {"status": "ignored"}

    async def handle_fisherman_message(self, incoming: IncomingMessage) -> dict[str, Any]:
        await self.mirror_to_founder("INBOUND", incoming.from_phone, incoming.text)

        signal = parse_stock_signal(incoming.text)
        if signal.product:
            fisherman_record = self.memory.get_fisherman(incoming.from_phone)
            if fisherman_record:
                fisherman_record.reliability_score = min(fisherman_record.reliability_score + 0.05, 1.0)
                self.memory.upsert_fisherman(fisherman_record)

        return {
            "status": "processed",
            "signal": {
                "product": signal.product,
                "quantity_kg": signal.quantity_kg,
                "confidence": signal.confidence,
            },
        }

    async def process_unfulfilled_orders(self) -> dict[str, int]:
        orders = await self.shopify.fetch_unfulfilled_orders()
        messages_sent = 0

        for order in orders:
            order_id = str(order.get("id", ""))
            line_items = order.get("line_items", [])
            for item in line_items:
                product_name = str(item.get("name", "")).lower()
                quantity = item.get("quantity", 0)
                fisherman_phone = self._select_best_fisherman(product_name)
                if not fisherman_phone:
                    continue

                self.active_order_by_fisherman[fisherman_phone] = order_id
                msg = (
                    f"Need {quantity} units of {item.get('name', 'fish')} for order {order_id}. "
                    "Can supply today?"
                )
                sent = await self.send_to_fisherman(fisherman_phone, msg)
                if sent:
                    messages_sent += 1

        return {"orders": len(orders), "messages_sent": messages_sent}
