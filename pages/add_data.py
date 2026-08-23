import streamlit as st
from auth import check_password
from mapping_store import load_mapping, add_client

st.set_page_config(
    page_title="Add Data - MIS Automation",
    page_icon="➕",
    layout="wide"
)

if not check_password():
    st.stop()

st.markdown("""
<style>
.block-container { padding-top: 2rem; }
.page-title { font-size: 38px; font-weight: 800; }
.page-subtitle { color: var(--text-color); opacity: 0.65; font-size:18px; margin-bottom:30px; }
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
                mapping = load_mapping()

                if client_name in mapping:
                    st.warning(f"'{client_name}' already exists in the mapping.")
                else:
                    add_client(client_name, sheet_url)
                    st.success(f"✅ {client_name} added successfully.")
                    st.rerun()

            except Exception as e:
                st.error(f"Unable to update client mapping: {e}")

st.subheader("Current Clients")

try:
    mapping = load_mapping()

    if mapping:
        for name in mapping:
            st.write(f"• {name}")
    else:
        st.info("No clients are currently configured.")
except Exception as e:
    st.error(f"Unable to read client mapping: {e}")
