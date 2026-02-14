from dataclasses import dataclass
from typing import Any


@dataclass
class Fisherman:
    fisherman_id: str
    specialty: str
    reliability_score: float


@dataclass
class StockSignal:
    product: str | None
    quantity_kg: float | None
    confidence: float
    raw_text: str


@dataclass
class IncomingMessage:
    from_phone: str
    text: str
    metadata: dict[str, Any] | None = None
