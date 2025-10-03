# matcher.py

def normalize_amount(amount_str):
    """Convert $1,295.00 → 1295.00 as float"""
    return float(str(amount_str).replace("$", "").replace(",", "").strip())


def match_invoice_po(invoice, po):
    """
    Compare invoice and PO data in detail.
    invoice and po are dicts like:
    {
        "invoice_number": "INV-2024-001",
        "vendor": "TechSupply Co.",
        "total": "$1,295.00",
        "items": [
            {"description": "Monitor", "quantity": 2, "price": 250},
            {"description": "Keyboard", "quantity": 5, "price": 30}
        ]
    }
    """

    details = {
        "invoice_number": invoice.get("invoice_number"),
        "po_number": po.get("po_number"),
        "vendor_invoice": invoice.get("vendor"),
        "vendor_po": po.get("vendor"),
        "total_invoice": invoice.get("total"),
        "total_po": po.get("total"),
        "items_match": True,
        "line_items": []
    }

    # Vendor check
    if invoice.get("vendor", "").lower() != po.get("vendor", "").lower():
        details["vendor_match"] = False
    else:
        details["vendor_match"] = True

    # Total check
    if normalize_amount(invoice.get("total", 0)) != normalize_amount(po.get("total", 0)):
        details["total_match"] = False
    else:
        details["total_match"] = True

    # Line item check
    invoice_items = invoice.get("items", [])
    po_items = po.get("items", [])

    for inv_item in invoice_items:
        # Find matching item by description in PO
        po_item = next((p for p in po_items if p["description"].lower() == inv_item["description"].lower()), None)

        if po_item:
            qty_match = inv_item["quantity"] == po_item["quantity"]
            price_match = normalize_amount(inv_item["price"]) == normalize_amount(po_item["price"])
            item_match = qty_match and price_match
            if not item_match:
                details["items_match"] = False
        else:
            po_item = {"description": "-", "quantity": "-", "price": "-"}
            details["items_match"] = False
            qty_match = price_match = False

        details["line_items"].append({
            "description": inv_item["description"],
            "invoice_qty": inv_item["quantity"],
            "po_qty": po_item.get("quantity"),
            "invoice_price": inv_item["price"],
            "po_price": po_item.get("price"),
            "match": qty_match and price_match
        })

    # Overall match
    details["match"] = (
        details["vendor_match"] and
        details["total_match"] and
        details["items_match"]
    )

    return details
