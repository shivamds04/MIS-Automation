import streamlit as st
import json
import os
from pathlib import Path
from auth import check_password

st.set_page_config(
    page_title="Add Data - MIS Automation",
    page_icon="➕",
    layout="wide"
)

if not check_password():
    st.stop()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAPPING_FILE = Path(BASE_DIR).parent / "client_sheet_mapping.json"

st.markdown("""
<style>
.block-container { padding-top: 2rem; }
.page-title { font-size: 38px; font-weight: 800; }
.page-subtitle { color:#64748b; font-size:18px; margin-bottom:30px; }
.card {
    padding: 30px;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 18px;
    background: linear-gradient(180deg,#ffffff,#f8fafc);
    box-shadow: 0 14px 40px rgba(2,6,23,0.07);
}
</style>
""", unsafe_allow_html=True)

if st.button("← Back to MIS Automation", key="back_home_add"):
    st.switch_page("streamlit_app.py")
    
st.markdown("<div class='page-title'>➕ Add New Client MIS</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='page-subtitle'>Add a new client's Google Sheet mapping to the automation system.</div>",
    unsafe_allow_html=True
)

with st.container(border=True):
    client_name = st.text_input("Client Name", placeholder="Example: Tipsy Tiger")
    sheet_url = st.text_input(
        "Google Sheet URL",
        placeholder="https://docs.google.com/spreadsheets/d/..."
    )

    if st.button("➕ Add Client", type="primary", use_container_width=True):
        client_name = client_name.strip()
        sheet_url = sheet_url.strip()

        if not client_name or not sheet_url:
            st.error("Please enter both Client Name and Google Sheet URL.")
        elif not sheet_url.startswith("https://docs.google.com/spreadsheets/"):
            st.error("Please enter a valid Google Sheets URL.")
        else:
            try:
                if MAPPING_FILE.exists():
                    with MAPPING_FILE.open("r", encoding="utf-8") as f:
                        mapping = json.load(f)
                else:
                    mapping = {}

                if not isinstance(mapping, dict):
                    raise ValueError("client_sheet_mapping.json must contain Client Name -> Sheet URL mappings.")

                if client_name in mapping:
                    st.warning(f"'{client_name}' already exists in the mapping.")
                else:
                    mapping[client_name] = sheet_url

                    with MAPPING_FILE.open("w", encoding="utf-8") as f:
                        json.dump(mapping, f, indent=4, ensure_ascii=False)

                    st.success(f"✅ {client_name} added successfully.")
                    st.rerun()

            except Exception as e:
                st.error(f"Unable to update client mapping: {e}")

st.subheader("Current Clients")

try:
    if MAPPING_FILE.exists():
        with MAPPING_FILE.open("r", encoding="utf-8") as f:
            mapping = json.load(f)

        if mapping:
            for name in mapping:
                st.write(f"• {name}")
        else:
            st.info("No clients are currently configured.")
    else:
        st.info("client_sheet_mapping.json was not found.")
except Exception as e:
    st.error(f"Unable to read client mapping: {e}")
