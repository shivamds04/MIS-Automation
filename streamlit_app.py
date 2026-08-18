import os
import streamlit as st
import tempfile
from main import run_mis
from auth import check_password
import streamlit.components.v1 as components

st.set_page_config(
    page_title="MIS Automation System",
    page_icon="📊",
    layout="wide"
)

if not check_password():
    st.stop()


def render_footer():
    components.html(
        """
        <style>
        .portfolio-footer {
            margin-top: 80px;
            padding: 50px 0;
            background: #f8fafc;
            border-top: 1px solid rgba(0,0,0,0.08);
            text-align: center;
            font-family: Arial, sans-serif;
        }

        .footer-icons {
            display: flex;
            justify-content: center;
            gap: 22px;
            margin-bottom: 18px;
        }

        .footer-icons img {
            width: 22px;
            height: 22px;
            opacity: 0.85;
            transition: 0.3s;
        }

        .footer-icons img:hover {
            transform: scale(1.15);
            opacity: 1;
        }

        .footer-title {
            font-weight: 600;
            color: #0f172a;
            margin-bottom: 6px;
        }

        .footer-sub {
            font-size: 14px;
            color: #64748b;
        }
        </style>

        <div class="portfolio-footer">
            <div class="footer-icons">
                <a href="https://github.com/shivamds04" target="_blank">
                    <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/github.svg">
                </a>
                <a href="https://www.linkedin.com/in/shivam-singh-928508358?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app" target="_blank">
                    <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/linkedin.svg">
                </a>
                <a href="https://www.youtube.com/channel/UCv_XXIFLnYy0hxnpsNxwEQQ" target="_blank">
                    <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/youtube.svg">
                </a>
                <a href="https://www.instagram.com/techzen04?igsh=Y2Z3MGFteHRvbXA2" target="_blank">
                    <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/instagram.svg">
                </a>
            </div>

            <div class="footer-title">
                Shivam Singh — Data Science Student
            </div>

            <div class="footer-sub">
                © 2026 • Built with ❤️ and ☕ in a Room • Available for internships & projects
            </div>
        </div>
        """,
        height=260
    )


st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 0rem;
}

.app-title {
    font-size: 40px;
    font-weight: 800;
}

.app-subtitle {
    font-size: 18px;
    color: #64748b;
    margin-bottom: 35px;
}

/* Large navigation cards */
.nav-card-title {
    font-size: 27px;
    font-weight: 800;
    margin-top: 10px;
}

.nav-card-text {
    font-size: 16px;
    color: #64748b;
    margin-top: 8px;
}

/* Make the actual Streamlit buttons look like large cards */
.nav-card .stButton > button {
    min-height: 210px;
    width: 100%;
    border-radius: 18px;
    border: 1px solid rgba(0,0,0,0.07);
    background: linear-gradient(180deg,#ffffff,#f8fafc);
    color: #172033;
    box-shadow: 0 14px 40px rgba(2,6,23,0.08);
    font-size: 24px;
    font-weight: 800;
    transition: all 0.2s ease;
}

.nav-card .stButton > button:hover {
    transform: translateY(-4px);
    border-color: rgba(124,58,237,0.35);
    box-shadow: 0 18px 45px rgba(2,6,23,0.13);
}

.summary {
    background: #f1f5f9;
    padding: 16px;
    border-radius: 14px;
    margin-bottom: 10px;
}

.stButton > button {
    border-radius: 14px;
    padding: 12px;
    font-weight: 700;
}

.run-button .stButton > button {
    background: #1976D2 !important;
    color: white !important;
    border: none !important;
    min-height: 55px;
    font-size: 18px;
    font-weight: 700;
    border-radius: 12px;
}

.run-button .stButton > button:hover {
    background: #1565C0 !important;
    color: white !important;
}

.site-footer {
    margin-top: 80px;
    padding: 45px 20px;
    background: linear-gradient(180deg,#f8fafc,#ffffff);
    border-top: 1px solid rgba(0,0,0,0.06);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='app-title'>📊 MIS Automation System</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='app-subtitle'>Automated CSV → Google Sheet MIS Tool</div>",
    unsafe_allow_html=True
)

# ================= NAVIGATION CARDS =================
c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.markdown("<div class='nav-card'>", unsafe_allow_html=True)
    if st.button("➕\n\nAdd Data", key="add_data", use_container_width=True):
        st.switch_page("pages/add_data.py")
    st.markdown(
        "<div style='text-align:center;color:#64748b;font-size:15px;'>Add a new client's MIS to the system</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='nav-card'>", unsafe_allow_html=True)
    if st.button("🗑️\n\nRemove Data", key="remove_data", use_container_width=True):
        st.switch_page("pages/remove_data.py")
    st.markdown(
        "<div style='text-align:center;color:#64748b;font-size:15px;'>Remove an existing client's MIS mapping</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='nav-card'>", unsafe_allow_html=True)
    if st.button("📖\n\nGuidelines", key="guidelines", use_container_width=True):
        st.switch_page("pages/guidelines.py")
    st.markdown(
        "<div style='text-align:center;color:#64748b;font-size:15px;'>Learn how to use the MIS automation</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ================= STEP 1 =================
st.subheader("Step 1: Upload Main MIS CSV")

uploaded_file = st.file_uploader(
    "Choose Main MIS CSV file",
    type=["csv"],
    key="main_csv"
)

st.subheader("Step 2: Upload ETA CSV")

eta_uploaded_file = st.file_uploader(
    "Choose ETA CSV file",
    type=["csv"],
    key="eta_csv"
)

# ================= PROCESS FILES =================
if uploaded_file and eta_uploaded_file:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.getbuffer())
        csv_path = tmp.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(eta_uploaded_file.getbuffer())
        eta_csv_path = tmp.name

    st.subheader("Step 3: Run Automation")

    st.markdown("<div class='run-button'>", unsafe_allow_html=True)
    run_clicked = st.button(
        "🚀 Run MIS Automation",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if run_clicked:
        result = None
        try:
            with st.spinner("Processing MIS... Please wait"):
                result = run_mis(csv_path, eta_csv_path)
        except Exception as e:
            st.error(
                "Something went wrong while running the automation. "
                "This usually means a required CSV column is missing, "
                "or Google Sheets authentication failed."
            )
            with st.expander("Show technical details"):
                st.code(str(e))
        finally:
            # Clean up temp files regardless of success/failure
            for p in (csv_path, eta_csv_path):
                try:
                    os.remove(p)
                except OSError:
                    pass

        if result:
            if result.get("errors"):
                st.warning(result["status"])
            else:
                st.success(result["status"])

            st.subheader("Client-wise Summary")

            for item in result["summary"]:
                if item.get("failed"):
                    st.markdown(
                        f"""
                        <div class="summary" style="border-left:4px solid #dc2626;">
                            <b>{item['client']}</b> — ⚠️ Failed<br>
                            <span style="color:#dc2626;font-size:14px;">{item.get('error', 'Unknown error')}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="summary">
                            <b>{item['client']}</b><br>
                            Added: {item['added']} |
                            Duplicates: {item['duplicates']} |
                            Skipped: {item.get('skipped', 0)}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            c1, c2, c3 = st.columns(3)

            c1.metric("Total Clients", len(result["summary"]))
            c2.metric("Total Rows Added", result["total_added"])
            c3.metric("Failed Clients", len(result.get("errors", [])))

else:
    st.info("Please upload both Main MIS CSV and ETA CSV to continue.")

render_footer()
