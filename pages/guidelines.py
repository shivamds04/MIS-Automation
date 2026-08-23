import streamlit as st
from auth import check_password

st.set_page_config(
    page_title="Guidelines - MIS Automation",
    page_icon="📖",
    layout="wide"
)

if not check_password():
    st.stop()

st.markdown("""
<style>
.block-container { padding-top: 2rem; }
.page-title { font-size: 38px; font-weight: 800; }
.page-subtitle { color: var(--text-color); opacity: 0.65; font-size:18px; margin-bottom:30px; }
.step {
    padding: 20px;
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 15px;
    margin-bottom: 14px;
    background: var(--secondary-background-color);
    color: var(--text-color);
}
.step b {
    color: var(--text-color);
}
</style>



""", unsafe_allow_html=True)

if st.button("← Back to MIS Automation", key="back_home_guidelines"):
    st.switch_page("streamlit_app.py")
    
st.markdown("<div class='page-title'>📖 Guidelines</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='page-subtitle'>Follow these steps when using the MIS Automation System.</div>",
    unsafe_allow_html=True
)

st.markdown("""
<div class="step">
<b>Step 1 — Upload Main MIS CSV</b><br>
Upload the daily Main MIS CSV received from the operations team.
</div>

<div class="step">
<b>Step 2 — Upload ETA CSV</b><br>
Upload the ETA CSV containing <b>Consignment No</b> and <b>Actual ETA Date</b>.
The system uses the docket/consignment number to match ETA data.
</div>

<div class="step">
<b>Step 3 — Run Automation</b><br>
Click <b>🚀 Run MIS Automation</b> and wait until processing is completed.
</div>

<div class="step">
<b>Step 4 — Check Client-wise MIS</b><br>
The system processes each configured client separately and updates its Google Sheet.
</div>
""", unsafe_allow_html=True)

st.subheader("Important Points")

st.markdown("""
- Do not rename the required columns in the Main MIS CSV.
- ETA CSV should contain **Consignment No** and **Actual ETA Date**.
- Client names in the Main MIS should match the names configured in the client mapping.
- Keep the Google Sheet accessible to the configured service account (mis-bot@mis-automation-485003.iam.gserviceaccount.com).
- The **Remove Data** option removes only the client mapping; it does not delete the Google Sheet.
- Before changing client mappings, make sure the Google Sheet URL is correct.
""")

st.subheader("Adding a New Client")

st.markdown("""
1. Open **➕ Add Data**.
2. Enter the exact client name used in the Main MIS.
3. Paste the client's Google Sheet URL.
4. Click **Add Client**.
5. Return to the home page and run the MIS normally.
""")

st.subheader("Removing a Client")

st.markdown("""
1. Open **🗑️ Remove Data**.
2. Select the client.
3. Confirm the removal.
4. Click **Remove Client**.
""")
