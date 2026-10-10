import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from invoice_service import DeveloperOrder, invoice_html


def test_invoice_total_and_rendered_business_line():
    order = DeveloperOrder("DEV-7", "Solo Studio", "CI minutes", 4, 2.25)
    assert order.total == 9.0
    html = invoice_html(order)
    assert "CI minutes x 4 @ 2.25" in html
    assert "Total: 9.00" in html
