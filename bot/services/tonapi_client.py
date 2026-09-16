import aiohttp
from typing import Dict, Any, Optional


class TonAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://tonapi.io/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }

    async def get_nft_item(self, address: str) -> Optional[Dict[str, Any]]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.base_url}/nfts/{address}") as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def get_account_nfts(
            self,
            account_address: str,
            collection: str = None) -> list:
        # Get NFTs for an account. If collection is specified, filter by it.
        url = f"{self.base_url}/accounts/{account_address}/nfts"
        if collection:
            url += f"?collection={collection}"

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("nft_items", [])
                return []
