"""
Shared authentication module for MIS Automation System.
Provides password protection for all pages.
"""

import streamlit as st


def check_password():
    """
    Returns True only if the correct password has been entered.
    Blocks access to the rest of the app until then.
    
    Call this at the very top of any Streamlit page (after set_page_config)
    to protect it from unauthorized access.
    """

    def password_entered():
        try:
            correct = st.secrets.get("APP_PASSWORD", None)
        except Exception:
            correct = None

        if correct is None:
            st.session_state["password_correct"] = False
            st.session_state["password_missing_config"] = True
            return

        if st.session_state.get("password_input", "") == correct:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.markdown("### 🔒 MIS Automation System")
    st.text_input(
        "Enter password to continue",
        type="password",
        key="password_input",
        on_change=password_entered,
    )

    if st.session_state.get("password_missing_config"):
        st.error(
            "No app password has been configured. This app is locked until "
            "APP_PASSWORD is set in .streamlit/secrets.toml (local) or the "
            "app's Secrets settings (Streamlit Cloud)."
        )
    elif "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Incorrect password.")

    return False
