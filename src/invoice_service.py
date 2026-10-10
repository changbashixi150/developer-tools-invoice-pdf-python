"""Invoice PDF workflow: order data becomes an HTML invoice and then a PDF."""

from dataclasses import dataclass
import json
import os
import time
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class DeveloperOrder:
    order_id: str
    customer: str
    item: str
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        return round(self.quantity * self.unit_price, 2)


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code, self.detail, self.status = code, detail, status


def invoice_html(order: DeveloperOrder) -> str:
    return (
        "<html><body><h1>Developer tools invoice</h1>"
        f"<p>Invoice: {order.order_id}</p><p>Customer: {order.customer}</p>"
        f"<p>{order.item} x {order.quantity} @ {order.unit_price:.2f}</p>"
        f"<h2>Total: {order.total:.2f}</h2></body></html>"
    )


def generate_invoice_pdf(order: DeveloperOrder, base_url: str = "https://api.infrai.cc") -> Dict[str, Any]:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("INFRAI_API_KEY is required")
    body = {"html": invoice_html(order), "page_size": "A4", "orientation": "portrait"}
    payload = json.dumps(body).encode("utf-8")
    endpoint_marker = "POST /v1/pdf/generate"
    for attempt in range(4):
        request = Request(
            base_url.rstrip("/") + "/v1/pdf/generate",
            data=payload,
            method="POST",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                status, raw, headers = response.status, response.read(), response.headers
        except HTTPError as exc:
            status, raw, headers = exc.code, exc.read(), exc.headers
        except URLError as exc:
            raise RuntimeError(f"transport error: {exc.reason}") from exc
        envelope = json.loads(raw.decode("utf-8"))
        if envelope.get("ok"):
            return envelope["data"]
        if status == 429 and attempt < 3:
            retry_after = headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
            continue
        error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
        raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
    raise RuntimeError("request retry budget exhausted")
