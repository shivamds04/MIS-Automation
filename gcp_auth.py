"""
Shared Google authentication module.
Loads service account credentials from Streamlit secrets (cloud) or a
local JSON file (when running locally), and returns an authorized
gspread client.
"""

import os
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_gspread_client():
    """Returns an authorized gspread client, using cloud secrets if
    available, otherwise falling back to a local credentials file."""

    if "gcp_service_account" in st.secrets:
        service_account_info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES,
        )
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        service_account_file = os.path.join(base_dir, "credentials", "service_account.json")
        if not os.path.exists(service_account_file):
            raise FileNotFoundError(
                "Google service account credentials not found. "
                "Locally: place the file at credentials/service_account.json. "
                "On Streamlit Cloud: add a [gcp_service_account] section in Secrets."
            )
        creds = Credentials.from_service_account_file(
            service_account_file,
            scopes=SCOPES,
        )

    return gspread.authorize(creds)
