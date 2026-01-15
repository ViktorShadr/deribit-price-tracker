import unittest
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import inspect

from app.main import app
from app.db.deps import get_db


def _override_get_db():
    """Dependency override: возвращает заглушку вместо реальной SQLAlchemy Session."""
    yield object()


class ApiTests(unittest.IsolatedAsyncioTestCase):
    """Unit-тесты HTTP API: проверяем контракт роутов, не трогая реальную БД."""

    async def asyncSetUp(self):
        """Подготовка тестового клиента и overrides зависимостей перед каждым тестом."""
        self._prev_overrides = dict(app.dependency_overrides)
        app.dependency_overrides[get_db] = _override_get_db

        transport_kwargs = {"app": app}
        if "lifespan" in inspect.signature(httpx.ASGITransport.__init__).parameters:
            transport_kwargs["lifespan"] = "on"

        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(**transport_kwargs),
            base_url="http://test",
        )

    async def asyncTearDown(self):
        """Освобождение ресурсов и очистка overrides после каждого теста."""
        await self.client.aclose()
        app.dependency_overrides = self._prev_overrides

    async def test_health_ok(self):
        """GET /health возвращает 200 и ожидаемый JSON со статусом сервиса."""
        r = await self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"status": "ok"})

    async def test_prices_requires_ticker_returns_422(self):
        """GET /prices без обязательного query-параметра ticker возвращает 422."""
        r = await self.client.get("/prices")
        self.assertEqual(r.status_code, 422)
        self.assertIn("detail", r.json())

    async def test_latest_requires_ticker_returns_422(self):
        """GET /prices/latest без обязательного query-параметра ticker возвращает 422."""
        r = await self.client.get("/prices/latest")
        self.assertEqual(r.status_code, 422)
        self.assertIn("detail", r.json())

    async def test_by_date_requires_ticker_returns_422(self):
        """GET /prices/by-date без обязательного query-параметра ticker возвращает 422."""
        r = await self.client.get("/prices/by-date", params={"from_ts": 0, "to_ts": 1})
        self.assertEqual(r.status_code, 422)
        self.assertIn("detail", r.json())

    async def test_by_date_requires_from_to_returns_422(self):
        """GET /prices/by-date без from_ts/to_ts возвращает 422 (валидация query-параметров)."""
        r = await self.client.get("/prices/by-date", params={"ticker": "btc_usd"})
        self.assertEqual(r.status_code, 422)
        self.assertIn("detail", r.json())

    async def test_by_date_validation_from_gt_to_returns_400(self):
        """GET /prices/by-date возвращает 400 при from_ts > to_ts."""
        r = await self.client.get(
            "/prices/by-date",
            params={"ticker": "btc_usd", "from_ts": 10, "to_ts": 1},
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["detail"], "from_ts must be <= to_ts")

    @patch(
        "app.api.routes.PriceService.get_by_date",
        return_value=[
            SimpleNamespace(
                ticker="btc_usd", price=Decimal("42000.12345678"), ts=1700000000
            ),
            SimpleNamespace(
                ticker="btc_usd", price=Decimal("42010.00000000"), ts=1700000060
            ),
        ],
    )
    async def test_by_date_returns_list_when_range_is_valid(self, _mock_get_by_date):
        """GET /prices/by-date возвращает список при валидном диапазоне."""
        r = await self.client.get(
            "/prices/by-date",
            params={"ticker": "btc_usd", "from_ts": 1700000000, "to_ts": 1700000060},
        )
        self.assertEqual(r.status_code, 200)

        _mock_get_by_date.assert_called_once_with("btc_usd", 1700000000, 1700000060)

        data = r.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["ticker"], "btc_usd")
        self.assertEqual(data[0]["ts"], 1700000000)
        self.assertIn("price", data[0])

    @patch(
        "app.api.routes.PriceService.get_all",
        return_value=[
            SimpleNamespace(
                ticker="btc_usd", price=Decimal("42000.12345678"), ts=1700000000
            ),
            SimpleNamespace(
                ticker="btc_usd", price=Decimal("42010.00000000"), ts=1700000060
            ),
        ],
    )
    async def test_prices_returns_list(self, _mock_get_all):
        """GET /prices возвращает список цен по тикеру (happy path)."""
        r = await self.client.get("/prices", params={"ticker": "btc_usd"})
        self.assertEqual(r.status_code, 200)

        _mock_get_all.assert_called_once_with("btc_usd")

        data = r.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["ticker"], "btc_usd")
        self.assertEqual(data[0]["ts"], 1700000000)
        self.assertIn("price", data[0])

    @patch("app.api.routes.PriceService.get_all", return_value=[])
    async def test_prices_returns_empty_list_when_no_rows(self, _mock_get_all):
        """GET /prices возвращает пустой список, если данных нет."""
        r = await self.client.get("/prices", params={"ticker": "btc_usd"})
        self.assertEqual(r.status_code, 200)

        _mock_get_all.assert_called_once_with("btc_usd")
        self.assertEqual(r.json(), [])

    @patch("app.api.routes.PriceService.get_latest", return_value=None)
    async def test_latest_returns_404_when_no_data(self, _mock_get_latest):
        """GET /prices/latest возвращает 404, если данных нет."""
        r = await self.client.get("/prices/latest", params={"ticker": "btc_usd"})
        self.assertEqual(r.status_code, 404)

        _mock_get_latest.assert_called_once_with("btc_usd")
        self.assertEqual(r.json()["detail"], "No data for this ticker")

    @patch(
        "app.api.routes.PriceService.get_latest",
        return_value=SimpleNamespace(
            ticker="btc_usd", price=Decimal("42000.12345678"), ts=1700000000
        ),
    )
    async def test_latest_returns_200_when_data_exists(self, _mock_get_latest):
        """GET /prices/latest возвращает 200 и объект цены, если данные существуют."""
        r = await self.client.get("/prices/latest", params={"ticker": "btc_usd"})
        self.assertEqual(r.status_code, 200)

        _mock_get_latest.assert_called_once_with("btc_usd")

        data = r.json()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["ticker"], "btc_usd")
        self.assertEqual(data["ts"], 1700000000)
        self.assertIn("price", data)
