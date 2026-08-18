import json
import os
import re
from datetime import datetime, timedelta

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from gspread_formatting import Border, Borders, CellFormat, format_cell_range


# ============================================================
# HELPERS
# ============================================================

def norm(value):
    if value is None or pd.isna(value):
        return ""
    text = re.sub(r"\s+", " ", str(value).strip())
    if text.casefold() in {"nan", "none", "nat"}:
        return ""
    return text.casefold()


def docket_key(value):
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if not text or text.casefold() in {"nan", "none", "nat"}:
        return ""
    if re.fullmatch(r"-?\d+\.0+", text):
        text = text.split(".")[0]
    return text


def col_letter(n):
    result = ""
    while n:
        n, r = divmod(n - 1, 26)
        result = chr(65 + r) + result
    return result


def parse_date(value):
    if value is None or str(value).strip() == "":
        return None
    value = pd.to_datetime(value, dayfirst=True, errors="coerce")
    return None if pd.isna(value) else value.to_pydatetime()


def date_text(value):
    value = pd.to_datetime(value, dayfirst=True, errors="coerce")
    return "" if pd.isna(value) else value.strftime("%d-%b-%y")


def header_index(headers, name):
    target = norm(name)
    for i, h in enumerate(headers):
        if norm(h) == target:
            return i
    return None


# ============================================================
# MAIN
# ============================================================

def run_mis(csv_path, eta_csv_path):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MAPPING_FILE = os.path.join(BASE_DIR, "client_sheet_mapping.json")
    SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "credentials", "service_account.json")

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    # ---------------- AUTH ----------------
    # On Streamlit Cloud, credentials come from st.secrets (set in the
    # app's Secrets settings). Locally, they come from the JSON file in
    # credentials/. This lets the same code run in both places.
    if "gcp_service_account" in st.secrets:
        service_account_info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES,
        )
    else:
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(
                "Google service account credentials not found. "
                "Locally: place the file at credentials/service_account.json. "
                "On Streamlit Cloud: add a [gcp_service_account] section in Secrets."
            )
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES,
        )
    gc = gspread.authorize(creds)

    # ---------------- MAIN CSV ----------------
    df = pd.read_csv(csv_path, low_memory=False)
    df.columns = [str(c).strip().casefold() for c in df.columns]

    required = [
        "docket date",
        "consignment number",
        "consignor company name",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            "Main MIS CSV missing required columns: " + ", ".join(missing)
        )

    df["docket date"] = pd.to_datetime(
        df["docket date"], dayfirst=True, errors="coerce"
    )

    # ---------------- ETA CSV ----------------
    eta_df = pd.read_csv(eta_csv_path, low_memory=False)
    eta_df.columns = [str(c).strip().casefold() for c in eta_df.columns]

    if "consignment no" not in eta_df.columns:
        raise ValueError("ETA CSV column 'Consignment No' was not found.")
    if "actual eta date" not in eta_df.columns:
        raise ValueError("ETA CSV column 'Actual ETA Date' was not found.")

    eta_lookup = {}
    for _, r in eta_df.iterrows():
        d = docket_key(r.get("consignment no", ""))
        if not d:
            continue
        eta = date_text(r.get("actual eta date", ""))
        if eta:
            eta_lookup[d] = eta

    # ---------------- CLIENT MAP ----------------
    # client_sheet_mapping.json is user-editable data (via Add/Remove Data
    # pages), so it isn't meant to be a secret. But it's gitignored, so on
    # a fresh cloud deploy it won't exist yet — seed it from secrets once
    # so the app doesn't crash on first run.
    if not os.path.exists(MAPPING_FILE) and "client_sheet_mapping" in st.secrets:
        with open(MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(dict(st.secrets["client_sheet_mapping"]), f, indent=4, ensure_ascii=False)

    if not os.path.exists(MAPPING_FILE):
        raise FileNotFoundError(
            "client_sheet_mapping.json not found. Locally: create it in the "
            "project root. On Streamlit Cloud: add a [client_sheet_mapping] "
            "section in Secrets, or use the Add Data page after first deploy."
        )

    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        client_map = json.load(f)

    if not isinstance(client_map, dict):
        raise ValueError("client_sheet_mapping.json must be Client Name -> Sheet URL.")

    MAP = {
        "Docket No": "consignment number",
        "Docket Date": "docket date",
        "From Branch": "pickup branch code",
        "From City": "consignor city",
        "To Branch": "original del branch code",
        "To City": "consignee city",
        "Consignor Name": "consignor company name",
        "Consignee Name": "consignee company name",
        "From Pincode": "consignor pin",
        "To Pincode": "consignee pin",
        "No of Boxes": "total packages",
        "Invoice Value": "cn invoice value",
        "Act Wt": "actual weight",
        "Ch. Wt": "chargeable wt",
        "Current Status": "current location",
        "Invoice No": "product invoice#",
    }
    map_norm = {norm(k): v for k, v in MAP.items()}

    summary = []
    errors = []
    total_added = 0

    # ========================================================
    # EACH CLIENT IS PROCESSED INDEPENDENTLY
    # ========================================================
    for client_name, sheet_url in client_map.items():
        try:
            sh = gc.open_by_url(sheet_url).sheet1
            sheet_data = sh.get_all_values()

            if not sheet_data:
                raise ValueError(f"{client_name}: sheet has no header row.")

            headers = sheet_data[0]
            docket_idx = header_index(headers, "Docket No")
            date_idx = header_index(headers, "Docket Date")
            sno_idx = header_index(headers, "S. No.")
            eta_idx = header_index(headers, "ETA")

            if docket_idx is None:
                raise ValueError(f"{client_name}: 'Docket No' column not found.")
            if date_idx is None:
                raise ValueError(f"{client_name}: 'Docket Date' column not found.")

            # Existing data belongs to THIS client only.
            existing_dockets = set()
            existing_dates = []

            for row in sheet_data[1:]:
                if docket_idx < len(row):
                    d = docket_key(row[docket_idx])
                    if d:
                        existing_dockets.add(d)
                if date_idx < len(row):
                    dt = parse_date(row[date_idx])
                    if dt:
                        existing_dates.append(dt)

            # Keep the original date-window idea, but use >= so new
            # dockets from the same latest date are not lost.
            if existing_dates:
                last_date = max(existing_dates)
            else:
                valid_dates = df["docket date"].dropna()
                last_date = (
                    valid_dates.min().to_pydatetime() - timedelta(days=1)
                    if not valid_dates.empty else datetime.min
                )

            client_mask = df["consignor company name"].map(norm) == norm(client_name)
            date_mask = df["docket date"].notna() & (
                df["docket date"] >= pd.Timestamp(last_date)
            )
            cdf = df[client_mask & date_mask].copy()

            rows_to_add = []
            new_dockets = set()
            added_count = 0
            duplicate_count = 0
            skipped_count = 0

            # ---------------- BUILD ROWS ----------------
            for _, r in cdf.iterrows():
                docket = docket_key(r.get("consignment number", ""))

                if not docket:
                    skipped_count += 1
                    continue

                if docket in existing_dockets:
                    duplicate_count += 1
                    continue

                row = []
                for sheet_header in headers:
                    h = norm(sheet_header)

                    if h == norm("S. No."):
                        row.append("")

                    elif h == norm("ETA"):
                        row.append(eta_lookup.get(docket, ""))

                    elif h in map_norm:
                        value = r.get(map_norm[h], "")
                        if pd.isna(value):
                            value = ""
                        elif h == norm("Docket No"):
                            value = docket
                        elif h == norm("Docket Date"):
                            value = date_text(value)
                        row.append(value)

                    else:
                        row.append("")

                rows_to_add.append(row)
                new_dockets.add(docket)
                added_count += 1

            # ---------------- APPEND / SORT / FORMAT ----------------
            if rows_to_add:
                sh.append_rows(rows_to_add, value_input_option="USER_ENTERED")

                last_col = col_letter(len(headers))
                sh.sort(
                    (date_idx + 1, "asc"),
                    range=f"A2:{last_col}{sh.row_count}",
                )

                all_rows = sh.get_all_values()

                # S. No. after sort
                if sno_idx is not None:
                    updates = []
                    sno_col = col_letter(sno_idx + 1)
                    for row_no in range(2, len(all_rows) + 1):
                        updates.append({
                            "range": f"{sno_col}{row_no}",
                            "values": [[row_no - 1]],
                        })
                    if updates:
                        sh.batch_update(updates)

                # ETA for ALL rows whose docket exists in ETA CSV.
                # This means old rows also get ETA filled if available.
                if eta_idx is not None:
                    eta_updates = []
                    eta_col = col_letter(eta_idx + 1)

                    for row_no, row in enumerate(all_rows[1:], start=2):
                        if docket_idx >= len(row):
                            continue
                        docket = docket_key(row[docket_idx])
                        eta = eta_lookup.get(docket, "")
                        if eta:
                            current = row[eta_idx].strip() if eta_idx < len(row) else ""
                            if current != eta:
                                eta_updates.append({
                                    "range": f"{eta_col}{row_no}",
                                    "values": [[eta]],
                                })

                    if eta_updates:
                        sh.batch_update(eta_updates)

                # Border ONLY on rows which actually contain data.
                # Header is excluded. Blank rows are excluded.
                final_rows = sh.get_all_values()
                fmt = CellFormat(
                    borders=Borders(
                        top=Border("SOLID"),
                        bottom=Border("SOLID"),
                        left=Border("SOLID"),
                        right=Border("SOLID"),
                    )
                )

                start = None
                end = None
                for row_no, row in enumerate(final_rows[1:], start=2):
                    has_data = any(str(v).strip() for v in row)
                    if has_data:
                        if start is None:
                            start = row_no
                        end = row_no
                    elif start is not None:
                        format_cell_range(sh, f"A{start}:{last_col}{end}", fmt)
                        start = None
                        end = None

                if start is not None:
                    format_cell_range(sh, f"A{start}:{last_col}{end}", fmt)

            summary.append({
                "client": client_name,
                "added": added_count,
                "duplicates": duplicate_count,
                "skipped": skipped_count,
            })
            total_added += added_count

        except Exception as e:
            # Don't let one bad client (bad URL, permissions, missing
            # column, etc.) stop the rest of the clients from processing.
            errors.append({"client": client_name, "error": str(e)})
            summary.append({
                "client": client_name,
                "added": 0,
                "duplicates": 0,
                "skipped": 0,
                "failed": True,
                "error": str(e),
            })

    status = "MIS Completed Successfully" if not errors else "MIS Completed With Errors"

    return {
        "status": status,
        "total_added": total_added,
        "summary": summary,
        "errors": errors,
    }
