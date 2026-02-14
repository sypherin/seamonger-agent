import re

from src.models import StockSignal


PRODUCT_ALIASES: dict[str, str] = {
    "bawal": "bawal",
    "kembung": "kembung",
    "selar": "selar",
    "siakap": "siakap",
    "snapper": "snapper",
    "ikan": "ikan",
}


def parse_stock_signal(text: str) -> StockSignal:
    normalized = text.strip().lower()

    quantity_match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kilo|kilogram)?", normalized)
    quantity_kg = float(quantity_match.group(1)) if quantity_match else None

    product = None
    for alias, canonical in PRODUCT_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", normalized):
            product = canonical
            break

    availability_keywords = ["ada", "have", "got", "ready", "stock"]
    confidence = 0.1
    if any(keyword in normalized for keyword in availability_keywords):
        confidence += 0.5
    if quantity_kg is not None:
        confidence += 0.2
    if product is not None:
        confidence += 0.2

    return StockSignal(
        product=product,
        quantity_kg=quantity_kg,
        confidence=min(confidence, 1.0),
        raw_text=text,
    )
