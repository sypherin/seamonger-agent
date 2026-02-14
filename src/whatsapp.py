import httpx


class WhatsAppClient:
    def __init__(self, api_url: str, api_token: str) -> None:
        self.api_url = api_url.rstrip("/") if api_url else ""
        self.api_token = api_token

    async def send_message(self, to_phone: str, text: str) -> None:
        if not self.api_url:
            return

        headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        payload = {"to": to_phone, "message": text}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(f"{self.api_url}/messages", json=payload, headers=headers)
            response.raise_for_status()
