from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import httpx


class DeribitError(RuntimeError):
    """Ошибка при обращении к Deribit API."""


@dataclass(frozen=True)
class DeribitClient:
    base_url: str = "https://test.deribit.com/api/v2"
    timeout_s: float = 10.0

    def get_index_price(self, index_name: str) -> float:
        """
        Возвращает текущую index price для index_name (например, btc_usd / eth_usd).
        Deribit public endpoints не требуют авторизации. :contentReference[oaicite:0]{index=0}
        """
        url = f"{self.base_url}/public/get_index_price"
        params = {"index_name": index_name}

        with httpx.Client(timeout=self.timeout_s) as client:
            resp = client.get(url, params=params)

        if resp.status_code != 200:
            raise DeribitError(f"HTTP {resp.status_code}: {resp.text}")

        data = resp.json()

        # Deribit API может вернуть {"error": {...}} вместо result
        if "error" in data and data["error"]:
            raise DeribitError(f"Deribit error: {data['error']}")

        result = data.get("result")
        if result is None or "index_price" not in result:
            raise DeribitError(f"Unexpected response format: {data}")

        return float(result["index_price"])

    def get_index_prices(self, index_names: Iterable[str]) -> dict[str, float]:
        """
        Удобный метод: получить несколько индексов подряд.
        (Параллелить тут не нужно — 2 запроса/мин.)
        """
        return {name: self.get_index_price(name) for name in index_names}
