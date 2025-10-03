#frontend/app.py
import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://127.0.0.1:8000"

st.title("📑 Invoice & PO Matcher")

# ----------------------------
# Initialize session state
# ----------------------------
if "uploaded_invoices" not in st.session_state:
    st.session_state.uploaded_invoices = []

if "uploaded_pos" not in st.session_state:
    st.session_state.uploaded_pos = []

# ----------------------------
# Function to show comparison result
# ----------------------------
def show_comparison_result(results):
    if results["match"]:
        st.markdown(f"### ✅ Invoice {results['invoice_number']} matches PO {results['po_number']}")
        st.success(f"Vendor name matches: {results['vendor_invoice']}")
        st.success(f"Total amount: {results['total_invoice']}")
    else:
        st.markdown(f"### ❌ Mismatch")
        st.error(f"Invoice: {results['invoice_number']} | Vendor: {results['vendor_invoice']}")
        st.error(f"PO: {results['po_number']} | Vendor: {results['vendor_po']}")
        st.error(f"Invoice total: {results['total_invoice']}")
        st.error(f"PO total: {results['total_po']}")

    if results.get("line_items"):
        st.markdown("#### 📋 Items")
        df = pd.DataFrame(results["line_items"])
        # Highlight mismatches
        def highlight_row(row):
            color = "background-color: #d4edda" if row["match"] else "background-color: #f8d7da"
            return [color]*len(row)
        st.dataframe(df.style.apply(highlight_row, axis=1))

    # Final status
    if results.get("match"):
        st.markdown("### ✅ Status: APPROVED")
    else:
        st.markdown("### ❌ Status: NEEDS REVIEW")

# ----------------------------
# Upload Invoices
# ----------------------------
st.header("Upload Invoices")
invoice_files = st.file_uploader("Choose up to 3 Invoices", type=["pdf"], accept_multiple_files=True)
if invoice_files:
    for file in invoice_files:
        if file.name not in st.session_state.uploaded_invoices:
            files = {"file": (file.name, file.getvalue(), "application/pdf")}
            res = requests.post(f"{BACKEND_URL}/upload/invoice", files=files)
            st.session_state.uploaded_invoices.append(file.name)
            st.success(res.json()["message"])

# ----------------------------
# Upload Purchase Orders
# ----------------------------
st.header("Upload Purchase Orders")
po_files = st.file_uploader("Choose up to 3 POs", type=["pdf"], accept_multiple_files=True)
if po_files:
    for file in po_files:
        if file.name not in st.session_state.uploaded_pos:
            files = {"file": (file.name, file.getvalue(), "application/pdf")}
            res = requests.post(f"{BACKEND_URL}/upload/po", files=files)
            st.session_state.uploaded_pos.append(file.name)
            st.success(res.json()["message"])

# ----------------------------
# Compare Invoices with POs
# ----------------------------
if st.button("🔍 Compare Invoices with POs"):
    res = requests.get(f"{BACKEND_URL}/compare").json()
    st.subheader("Results")
    for r in res["results"]:
        show_comparison_result(r)
# ----------------------------
# Show Uploaded Invoices with Delete
# ----------------------------
st.subheader("Uploaded Invoices")
for file_name in st.session_state.uploaded_invoices.copy():  # use copy() to safely modify list
    col1, col2 = st.columns([3,1])
    col1.write(file_name)
    if col2.button(f"🗑 Remove {file_name}", key=f"remove-invoice-{file_name}"):
        try:
            res = requests.delete(f"{BACKEND_URL}/remove/invoice/{file_name}")
            st.warning(res.json()["message"])
        except Exception as e:
            st.error(f"Error removing file: {e}")
        # Remove from session state immediately
        st.session_state.uploaded_invoices.remove(file_name)

# ----------------------------
# Show Uploaded POs with Delete
# ----------------------------
st.subheader("Uploaded POs")
for file_name in st.session_state.uploaded_pos.copy():  # use copy() to safely modify list
    col1, col2 = st.columns([3,1])
    col1.write(file_name)
    if col2.button(f"🗑 Remove {file_name}", key=f"remove-po-{file_name}"):
        try:
            res = requests.delete(f"{BACKEND_URL}/remove/po/{file_name}")
            st.warning(res.json()["message"])
        except Exception as e:
            st.error(f"Error removing file: {e}")
        # Remove from session state immediately
        st.session_state.uploaded_pos.remove(file_name)

