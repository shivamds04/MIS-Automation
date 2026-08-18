import streamlit as st
import json
import os
from pathlib import Path
from auth import check_password

st.set_page_config(
    page_title="Remove Data - MIS Automation",
    page_icon="🗑️",
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
.warning {
    padding: 18px;
    border-radius: 12px;
    background: #fff7ed;
    border: 1px solid #fed7aa;
    color: #9a3412;
}
</style>
""", unsafe_allow_html=True)

if st.button("← Back to MIS Automation", key="back_home_remove"):
    st.switch_page("streamlit_app.py")
    
st.markdown("<div class='page-title'>🗑️ Remove Client MIS</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='page-subtitle'>Remove a client from the automation mapping.</div>",
    unsafe_allow_html=True
)

try:
    if MAPPING_FILE.exists():
        with MAPPING_FILE.open("r", encoding="utf-8") as f:
            mapping = json.load(f)
    else:
        mapping = {}

    if not isinstance(mapping, dict):
        raise ValueError("client_sheet_mapping.json must contain Client Name -> Sheet URL mappings.")

    if not mapping:
        st.info("No clients are currently configured.")
    else:
        client_name = st.selectbox(
            "Select Client",
            options=list(mapping.keys())
        )

        st.markdown(
            """
            <div class="warning">
            ⚠️ This only removes the client from the automation mapping.
            The actual Google Sheet will NOT be deleted.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        confirm = st.checkbox(
            f"I understand that '{client_name}' will be removed from the automation mapping."
        )

        if st.button("🗑️ Remove Client", type="primary", use_container_width=True):
            if not confirm:
                st.warning("Please confirm the removal first.")
            else:
                del mapping[client_name]

                with MAPPING_FILE.open("w", encoding="utf-8") as f:
                    json.dump(mapping, f, indent=4, ensure_ascii=False)

                st.success(f"✅ {client_name} removed successfully.")
                st.rerun()

except Exception as e:
    st.error(f"Unable to update client mapping: {e}")
