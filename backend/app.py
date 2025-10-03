#backend/app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from extractor import extract_invoice_data, extract_po_data
from matcher import match_invoice_po

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

invoices = []
purchase_orders = []


@app.post("/upload/invoice")
async def upload_invoice(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    data = extract_invoice_data(filepath)
    invoices.append({"filename": file.filename, "data": data})
    return {"message": f"Invoice {file.filename} uploaded", "data": data}


@app.post("/upload/po")
async def upload_po(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    data = extract_po_data(filepath)
    purchase_orders.append({"filename": file.filename, "data": data})
    return {"message": f"PO {file.filename} uploaded", "data": data}

@app.get("/compare")
async def compare_docs():
    results = []
    for inv in invoices:
        match_found = False
        for po in purchase_orders:
            details = match_invoice_po(inv["data"], po["data"])
            if details["match"]:
                match_found = True
                results.append(details)
                break
        if not match_found:
            # Even if no perfect match, return structured details
            results.append({
                "match": False,
                "invoice_number": inv["data"].get("invoice_number",""),
                "po_number": None,
                "vendor_invoice": inv["data"].get("vendor",""),
                "vendor_po": None,
                "total_invoice": inv["data"].get("total",""),
                "total_po": None,
                "items_match": False,
                "line_items": []
            })
    return {"results": results}


@app.delete("/remove/{doc_type}/{filename}")
async def remove_file(doc_type: str, filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Remove from memory
    global invoices, purchase_orders
    if doc_type == "invoice":
        invoices = [f for f in invoices if f["filename"] != filename]
    elif doc_type == "po":
        purchase_orders = [f for f in purchase_orders if f["filename"] != filename]
    else:
        raise HTTPException(status_code=400, detail="doc_type must be 'invoice' or 'po'")

    # Remove file from disk
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"message": f"{doc_type} {filename} removed"}
    else:
        return {"message": f"{doc_type} {filename} not found on disk (maybe already deleted)"}
