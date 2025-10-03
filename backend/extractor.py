#extractor.py
import re
from PyPDF2 import PdfReader

def read_pdf(filepath):
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        # normalize spaces and newlines
        text = " ".join(text.split())
        return text
    except Exception:
        return ""

def extract_invoice_data(filepath):
    text = read_pdf(filepath)
    invoice_match = re.search(r"INV-\d+", text)
    vendor_match = re.search(r"Vendor[:\s]+([A-Za-z0-9 &.,]+)", text)
    total_match = re.search(r"\$[\d,]+\.\d{2}", text)

    return {
        "invoice_number": invoice_match.group(0) if invoice_match else "Unknown",
        "vendor": vendor_match.group(1).strip() if vendor_match else "Unknown",
        "total": total_match.group(0) if total_match else "$0.00",
        "items": [
            # For now, leave empty; you can extend extraction later
        ]
    }

def extract_po_data(filepath):
    text = read_pdf(filepath)
    po_match = re.search(r"PO-\d+", text)
    vendor_match = re.search(r"Vendor[:\s]+([A-Za-z0-9 &.,]+)", text)
    total_match = re.search(r"\$[\d,]+\.\d{2}", text)

    return {
        "po_number": po_match.group(0) if po_match else "Unknown",
        "vendor": vendor_match.group(1).strip() if vendor_match else "Unknown",
        "total": total_match.group(0) if total_match else "$0.00",
        "items": [
            # For now, leave empty; you can extend extraction later
        ]
    }
