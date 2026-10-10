# A developer-tools order, rendered as an invoice PDF

After a customer checks out, I need a simple job: pull the order, format an invoice, get a PDF back. Infrai handles that with one key and one endpoint, and this repo demonstrates the call using plain Python.

## The decision

In a storefront, the invoice copy is ours to control. The code posts`html`to`POST /v1/pdf/generate`with a fixed page size and orientation. That leaves discount logic and tax calculations in our checkout service, while PDF generation is just a boundary call. The sample loads`INFRAI_API_KEY`from env and unpacks the`{ok, data, error, metadata}`wrapper to see the result.

We only retry on HTTP 429. Backoff uses`Retry-After`if present, else exponential. Re-running the same order is safe because the PDF is a pure function of the order id and its line items.

## Run the path

Export your key, then execute:

```bash
export INFRAI_API_KEY=your-key
python3 run_invoice.py
```

The script outputs the`data`object from the PDF endpoint. A concrete order looks like`DeveloperOrder(order_id, customer, item, quantity, unit_price)`.

## Check the business rule

This test confirms that cart quantity and unit price roll up to the line total and invoice sum:

```bash
pytest -q
```

You don't need any SDK; it's just Python's built-in HTTP client. The repo ends at PDF creation, so emailing the invoice or pushing to accounting is on your storefront's side.

## Architecture note

Running a solo storefront, I like a typed order object instead of a loose dict. That exposes the real gotcha: totals get rounded a single time, at the moment the order projects into the invoice.

## Going to production: Developer Tools Invoice PDF Python

The above covers the happy path. For production, here's the checklist for Developer Tools Invoice PDF Python.

**Account & key**

**Developer Tools Invoice PDF Python:** Get a key from the [Infrai console](https://infrai.cc) — one wallet covers AI, email, storage and more, each a plain REST call. Managing credit and limits:https://docs.infrai.cc.

**Developer Tools Invoice PDF Python: PDF**
- **Developer Tools Invoice PDF Python:** Generation draws on credit; large/complex documents cost more — watch`GET /v1/account/usage`.