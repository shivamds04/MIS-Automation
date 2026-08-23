"""
Client mapping storage — backed by a Google Sheet instead of a local
JSON file, so it survives Streamlit Cloud restarts/redeploys (which
wipe the local filesystem).

Requires a Google Sheet with two columns: "Client Name" and "Sheet URL",
shared with your service account email. Its URL goes in secrets as
MAPPING_SHEET_URL (or locally in .streamlit/secrets.toml).
"""

import streamlit as st
from gcp_auth import get_gspread_client


def _get_mapping_sheet():
    if "MAPPING_SHEET_URL" not in st.secrets:
        raise ValueError(
            "MAPPING_SHEET_URL not found in secrets. Create a Google Sheet "
            "with columns 'Client Name' and 'Sheet URL', share it with your "
            "service account email, and add its URL as MAPPING_SHEET_URL "
            "in Secrets."
        )
    gc = get_gspread_client()
    return gc.open_by_url(st.secrets["MAPPING_SHEET_URL"]).sheet1


def load_mapping():
    """Returns the client mapping as a dict: {client_name: sheet_url}."""
    sh = _get_mapping_sheet()
    rows = sh.get_all_values()

    if not rows:
        return {}

    # Skip header row
    mapping = {}
    for row in rows[1:]:
        if len(row) >= 2 and row[0].strip():
            mapping[row[0].strip()] = row[1].strip()
    return mapping


def save_mapping(mapping):
    """Overwrites the mapping sheet with the given dict."""
    sh = _get_mapping_sheet()
    sh.clear()
    rows = [["Client Name", "Sheet URL"]]
    for client_name, sheet_url in mapping.items():
        rows.append([client_name, sheet_url])
    sh.update(rows)


def add_client(client_name, sheet_url):
    mapping = load_mapping()
    mapping[client_name] = sheet_url
    save_mapping(mapping)


def remove_client(client_name):
    mapping = load_mapping()
    if client_name in mapping:
        del mapping[client_name]
        save_mapping(mapping)
