import json
from src.invoice_service import DeveloperOrder, generate_invoice_pdf


if __name__ == "__main__":
    order = DeveloperOrder("DEV-1001", "Acme Tools", "Build minutes", 3, 12.50)
    print(json.dumps(generate_invoice_pdf(order), indent=2))
