import os
import unittest
from unittest.mock import patch

import vants_clipper as vc


class FakeResp:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self.ok = 200 <= status_code < 300
        self._payload = payload
        self.headers = {"content-type": "application/json"}

    def json(self):
        return self._payload


class TestVantsClipper(unittest.TestCase):
    def test_version_a_tupla(self):
        self.assertGreater(vc.version_a_tupla("1.2.0"), vc.version_a_tupla("1.1.0"))
        self.assertGreater(vc.version_a_tupla("v1.10.0"), vc.version_a_tupla("v1.2.9"))
        self.assertEqual(vc.version_a_tupla("v1.1.0"), (1, 1, 0))

    def test_parse_mcp_sse_json(self):
        raw = 'event: message\ndata: {"jsonrpc":"2.0","result":{"ok":true}}\n\n'
        parsed = vc.parse_mcp_sse_json(raw)
        self.assertIsNotNone(parsed)
        self.assertTrue(parsed["result"]["ok"])

    def test_consumir_short_free_blocks_auto_upload(self):
        with patch.dict(os.environ, {"VANTS_API_TOKEN": "jwt_free"}, clear=False):
            with patch.object(vc, "requests") as mock_req:
                mock_req.post.return_value = FakeResp(
                    403,
                    {"ok": False, "error": "requiere_membresia", "detalle": "Requiere plan pago"},
                )
                ok, motivo, _ = vc.consumir_short_vants({})
                self.assertFalse(ok)
                self.assertIn("requiere_membresia", motivo)

    def test_consumir_short_pro_allows_within_daily_quota(self):
        with patch.dict(os.environ, {"VANTS_API_TOKEN": "jwt_pro"}, clear=False):
            with patch.object(vc, "requests") as mock_req:
                mock_req.post.return_value = FakeResp(
                    200,
                    {"ok": True, "quota": {"plan": "pro", "shorts": {"usados": 1, "limite": 3, "restantes": 2}}},
                )
                ok, motivo, quota = vc.consumir_short_vants({})
                self.assertTrue(ok)
                self.assertEqual(motivo, "ok")
                self.assertEqual(quota["shorts"]["restantes"], 2)

    def test_optimizar_con_vidiq_uses_vants_proxy_first(self):
        with patch.dict(os.environ, {"VANTS_API_TOKEN": "jwt_pro"}, clear=False):
            with patch.object(vc, "requests") as mock_req:
                mock_req.post.return_value = FakeResp(
                    200,
                    {
                        "ok": True,
                        "source": "vidiq_mcp",
                        "recommendedTitle": "Ace imposible en Ascent #valorant #shorts",
                        "description": "desc",
                        "tags": ["valorant", "shorts"],
                    },
                )
                seo = vc.optimizar_con_vidiq("Ace Ascent", "VALORANT", {"vidiq": {"activo": True}})
                self.assertEqual(seo["source"], "vidiq_mcp")
                self.assertIn("Ascent", seo["title"])


if __name__ == "__main__":
    unittest.main()
