import json

import httpx
import respx

from worker.gateway_client import GatewayClient


@respx.mock
def test_update_status_sends_camel_case_body_and_api_key_header() -> None:
    route = respx.patch("http://gateway.test/internal/documents/d1/status").mock(return_value=httpx.Response(200))
    client = GatewayClient(base_url="http://gateway.test")

    client.update_status("d1", "DONE", 3, None, correlation_id="corr-1")

    request = route.calls.last.request
    assert request.headers["X-Correlation-Id"] == "corr-1"
    assert "X-Internal-Api-Key" in request.headers
    body = json.loads(request.content)
    assert body == {"status": "DONE", "chunkCount": 3, "errorMessage": None}


@respx.mock
def test_update_status_includes_error_message_when_failed() -> None:
    route = respx.patch("http://gateway.test/internal/documents/d2/status").mock(return_value=httpx.Response(200))
    client = GatewayClient(base_url="http://gateway.test")

    client.update_status("d2", "FAILED", 0, "Unsupported file type", correlation_id="corr-2")

    body = json.loads(route.calls.last.request.content)
    assert body == {"status": "FAILED", "chunkCount": 0, "errorMessage": "Unsupported file type"}
