import urllib.request
import json

samples = [
    ("INVOICE #FIGMA-2026-921\nMerchant: Figma, Inc.\nDate: 2026-09-12\nFigma Professional Seat Annual Subscription\nTotal Amount: $180.00 USD", "sample_1.txt"),
    ("RECEIPT #AWS-8821\nMerchant: Amazon Web Services\nDate: 2026-08-31\nEC2 S3 and Tiger Data Cloud Compute Hosting\nTotal Amount: $245.50 USD", "sample_2.txt"),
    ("TAX INVOICE\nMerchant: WeWork\nDate: 2026-09-01\nDedicated Desk Coworking Pass Q3\nTotal Amount: $350.00 USD", "sample_3.txt"),
    ("CAFE RECEIPT\nMerchant: Blue Bottle Cafe\nDate: 2026-09-18\nClient Strategic Planning Business Lunch\nTotal Amount: $68.40 USD", "sample_4.txt"),
    ("SERVICE INVOICE #APP-991\nMerchant: Apple\nDate: 2026-09-22\nMacBook Pro Hardware Maintenance\nTotal Amount: $289.00 USD", "sample_5.txt"),
    ("TRIP RECEIPT\nMerchant: Uber\nDate: 2026-09-25\nClient Office Architecture Onsite Transfer\nTotal Amount: $48.20 USD", "sample_6.txt")
]

for text, fname in samples:
    req = urllib.request.Request(
        "https://receiptdesk-ai.onrender.com/api/receipts/parse-text",
        data=json.dumps({"raw_text": text, "filename": fname}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read())
            rcpt = res_data.get("receipt", {})
            print(f"Uploaded {fname}: Merchant={rcpt.get('merchant')}, Total={rcpt.get('total_amount')}, Deductible={rcpt.get('deductible_amount')}")
    except Exception as e:
        print("Error uploading", fname, e)

res = urllib.request.urlopen("https://receiptdesk-ai.onrender.com/api/analytics/summary")
s = json.loads(res.read())
print("FINAL SUMMARY:")
print(f"Total Expenses: ${s['total_expenses']:.2f}")
print(f"Tax Deductible: ${s['total_deductible']:.2f}")
print(f"Est Tax Savings: ${s['estimated_tax_savings']:.2f}")
