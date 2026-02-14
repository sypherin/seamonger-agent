from typing import Any

import httpx


class ShopifyClient:
    def __init__(self, store_domain: str, access_token: str, api_version: str) -> None:
        self.store_domain = store_domain
        self.access_token = access_token
        self.api_version = api_version

    async def fetch_unfulfilled_orders(self) -> list[dict[str, Any]]:
        if not self.store_domain or not self.access_token:
            return []

        url = (
            f"https://{self.store_domain}/admin/api/{self.api_version}/orders.json"
            "?status=open&fulfillment_status=unfulfilled&limit=50"
        )
        headers = {"X-Shopify-Access-Token": self.access_token}

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            payload = response.json()
        return payload.get("orders", [])
