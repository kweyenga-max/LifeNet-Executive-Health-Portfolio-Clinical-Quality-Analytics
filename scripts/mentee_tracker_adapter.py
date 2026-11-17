import os
import re
from datetime import date
import pandas as pd
import requests
import streamlit as st
import urllib3

from scripts.monitrac_adapter import _get_monitrac_credentials

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
MENTEE_SNAPSHOT_PATH = os.path.join(DATA_DIR, "monitrac_mentees_snapshot.csv.gz")

PROGRAM_UID = "NYY8hzVYv8f"
STAGE_UID = "mUbnQdn2XBO"
KENYA_OU_UID = "HfVjCurKxh2"

MODALITY_LABELS = {
    "centralized": "Centralized Training",
    "mentorship": "Onsite Mentorship",
    "support": "Virtual / Ad-hoc (WhatsApp & Phone)",
}

MENTOR_REGISTRY = {
    "newton-byegon": {"name": "Newton Byegon", "track": "Medical", "cohort": "Cohort 3"},
    "whyttney-claire": {"name": "Whyttney Claire", "track": "Medical", "cohort": "Cohort 3"},
    "joseph-kirori": {"name": "Joseph Kirori", "track": "Medical", "cohort": "Cohort 1 & 2"},
    "mary-wanyama": {"name": "Mary Wanyama", "track": "Management", "cohort": "Cohort 3"},
    "lewis-muriuki": {"name": "Lewis Muriuki", "track": "Management", "cohort": "Cohort 1 & 2"},
    "adrian-nyolde": {"name": "Adrian Nyolde", "track": "Management", "cohort": "Cohort 3"},
}

MODULE_LABELS = {
    "med-mod-1": "Med Mod 1: Foundations & Safe Care",
    "med-mod-2": "Med Mod 2: Maternal Health",
    "med-mod-3": "Med Mod 3: Newborn Care",
    "med-mod-4": "Med Mod 4: Child Health & Infectious",
    "med-mod-5": "Med Mod 5: NCDs & Clinical Quality",
    "mgt-mod-1": "Mgt Mod 1: Leadership & Governance",
    "mgt-mod-2": "Mgt Mod 2: Financial Management",
    "mgt-mod-3": "Mgt Mod 3: Pharmaceutical & Supply",
    "mgt-mod-4": "Mgt Mod 4: HMIS & Facility Admin",
}

MGT_LESSON_KEYWORDS = (
    "pharmaceutical",
    "admin-mgt",
    "financial-mgt",
    "hmis-moh",
    "leadership-governanace",
    "leadership-governance",
    "ordering-receiving",
    "recordkeeping-stockroom",
    "storage-organisation",
)


def _classify_curriculum(modules_raw: str, lessons_raw: str, mentor_track: str) -> tuple[str, str]:
    mods = [m.strip().lower() for m in str(modules_raw or "").split(",") if m.strip()]
    lessons = [l.strip().lower() for l in str(lessons_raw or "").split(",") if l.strip()]

    has_med = any(m.startswith("med-mod") for m in mods)
    has_mgt = any(m.startswith("mgt-mod") for m in mods)

    if not has_med and not has_mgt and lessons:
        has_mgt = any(any(k in l for k in MGT_LESSON_KEYWORDS) for l in lessons)
        has_med = any(not any(k in l for k in MGT_LESSON_KEYWORDS) for l in lessons)

    if not has_med and not has_mgt:
        if mentor_track == "Medical Mentors":
            has_med = True
        elif mentor_track == "Management Mentors":
            has_mgt = True
        elif mentor_track == "Joint (Medical + Management)":
            has_med, has_mgt = True, True

    if has_med and has_mgt:
        curr = "Dual Curriculum (Medical + Management)"
    elif has_med:
        curr = "Medical Curriculum"
    elif has_mgt:
        curr = "Management Curriculum"
    else:
        curr = "Unspecified"

    pretty_mods = [MODULE_LABELS.get(m, m.upper()) for m in mods]
    return curr, ", ".join(pretty_mods) if pretty_mods else "General / Unspecified"


def _classify_mentors(raw_trainer: str) -> tuple[str, str, str]:
    tokens = [t.strip().lower() for t in str(raw_trainer or "").split(",") if t.strip()]
    if not tokens:
        return "Unassigned", "Unassigned", "Unassigned"

    names, tracks, cohorts = [], set(), set()
    for tok in tokens:
        if tok in MENTOR_REGISTRY:
            info = MENTOR_REGISTRY[tok]
            names.append(info["name"])
            tracks.add(info["track"])
            cohorts.add(info["cohort"])
        else:
            pretty = " ".join(w.capitalize() for w in tok.replace("_", "-").split("-"))
            names.append(pretty)

    if tracks == {"Medical"}:
        track_lbl = "Medical Mentors"
    elif tracks == {"Management"}:
        track_lbl = "Management Mentors"
    elif "Medical" in tracks and "Management" in tracks:
        track_lbl = "Joint (Medical + Management)"
    else:
        track_lbl = "Other / Support Staff"

    if cohorts == {"Cohort 3"}:
        cohort_lbl = "Cohort 3"
    elif cohorts == {"Cohort 1 & 2"}:
        cohort_lbl = "Cohort 1 & 2"
    elif "Cohort 3" in cohorts and "Cohort 1 & 2" in cohorts:
        cohort_lbl = "Cross-Cohort (C1/2 + C3)"
    else:
        cohort_lbl = "Other"

    return ", ".join(names), track_lbl, cohort_lbl


def _build_beneficiary_uid(row: pd.Series) -> str:
    tei = str(row.get("tei", "") or "").strip()
    if tei and tei.lower() != "nan":
        return f"TEI:{tei}"
    id_num = re.sub(r"\W+", "", str(row.get("id_number", "") or "")).upper()
    if id_num and id_num != "NAN":
        return f"ID:{id_num}"
    fn = re.sub(r"\s+", " ", str(row.get("first_name", "") or "").strip().lower())
    ln = re.sub(r"\s+", " ", str(row.get("last_name", "") or "").strip().lower())
    ou = re.sub(r"\s+", " ", str(row.get("facility_name", "") or "").strip().lower())
    return f"NAME:{fn}_{ln}@{ou}"


@st.cache_data(ttl=3600, show_spinner=False)
def sync_monitrac_mentees(force_live: bool = False) -> pd.DataFrame:
    if not force_live and os.path.exists(MENTEE_SNAPSHOT_PATH):
        try:
            df_snap = pd.read_csv(MENTEE_SNAPSHOT_PATH, compression="gzip")
            if not df_snap.empty and "Curriculum" in df_snap.columns:
                return df_snap
        except Exception:
            pass

    base_url, username, password = _get_monitrac_credentials()
    if not base_url or not username or not password:
        if os.path.exists(MENTEE_SNAPSHOT_PATH):
            return pd.read_csv(MENTEE_SNAPSHOT_PATH, compression="gzip")
        return pd.DataFrame()

    dims = [
        f"ou:{KENYA_OU_UID}",
        "fjxKa1FBXHj",  # ProgTrac_type of activity (modality)
        "IDmCuuXlY7h",  # ProgTrac_Special Training
        "BHg8LLaoolq",  # First name
        "srPxZ5neKN8",  # Last Name
        "VOgAAr49GRA",  # ProgTrac Trainer
        "tQ77o1T5TuE",  # ProgTrac_Lessons
        "ABiGlWCsGye",  # ProgTrac_Module
        "InLMldiUBio",  # Gender
        "MdUwUhekwRQ",  # Position/Cadre
        "nDIEOZg66XB",  # Is a Sister
        "BhEi9vjZxzH",  # Program Phase
        "a0SOzfZXdMm",  # ID number
    ]

    all_rows = []
    headers = []
    page = 1
    end_yr = max(date.today().year, 2026)

    try:
        while True:
            params = [
                ("stage", STAGE_UID),
                ("displayProperty", "NAME"),
                ("outputType", "EVENT"),
                ("startDate", "2024-01-01"),
                ("endDate", f"{end_yr}-12-31"),
                ("pageSize", "500"),
                ("page", str(page)),
            ] + [("dimension", d) for d in dims]

            resp = requests.get(
                f"{base_url}/api/analytics/events/query/{PROGRAM_UID}.json",
                params=params,
                auth=(username, password),
                verify=False,
                timeout=35,
            )
            if resp.status_code != 200:
                break
            payload = resp.json()
            if not headers:
                headers = [h["name"] for h in payload.get("headers", [])]
            rows = payload.get("rows", [])
            if not rows:
                break
            all_rows.extend(rows)
            pager = payload.get("metaData", {}).get("pager", {})
            if page >= int(pager.get("pageCount", 1)):
                break
            page += 1
    except Exception as exc:
        print(f"Warning: Live MoniTrac Mentee Tracker pull failed ({exc}); using snapshot.")
        if os.path.exists(MENTEE_SNAPSHOT_PATH):
            return pd.read_csv(MENTEE_SNAPSHOT_PATH, compression="gzip")
        return pd.DataFrame()

    if not all_rows or not headers:
        if os.path.exists(MENTEE_SNAPSHOT_PATH):
            return pd.read_csv(MENTEE_SNAPSHOT_PATH, compression="gzip")
        return pd.DataFrame()

    df_raw = pd.DataFrame(all_rows, columns=headers)
    col_map = {
        "psi": "event_uid",
        "tei": "tei",
        "pi": "enrollment_uid",
        "eventdate": "event_date_raw",
        "ouname": "facility_name",
        "ounamehierarchy": "ou_hierarchy",
        "eventstatus": "event_status",
        "fjxKa1FBXHj": "modality_code",
        "IDmCuuXlY7h": "special_training",
        "BHg8LLaoolq": "first_name",
        "srPxZ5neKN8": "last_name",
        "VOgAAr49GRA": "trainer_raw",
        "tQ77o1T5TuE": "lessons",
        "ABiGlWCsGye": "modules",
        "InLMldiUBio": "gender_raw",
        "MdUwUhekwRQ": "cadre_raw",
        "nDIEOZg66XB": "is_sister",
        "BhEi9vjZxzH": "program_phase",
        "a0SOzfZXdMm": "id_number",
    }
    keep_cols = [c for c in col_map if c in df_raw.columns]
    df = df_raw[keep_cols].rename(columns=col_map).copy()

    df["event_dt"] = pd.to_datetime(df["event_date_raw"], errors="coerce")
    df = df[df["event_dt"].notna()].copy()
    df["event_date"] = df["event_dt"].dt.strftime("%Y-%m-%d")
    df["Year"] = df["event_dt"].dt.year.astype(int)
    df["Month_Num"] = df["event_dt"].dt.month.astype(int)
    df["Month_Label"] = df["event_dt"].dt.strftime("%B %Y")
    df["Year_Month"] = df["event_dt"].dt.strftime("%Y-%m")
    df["Quarter_Label"] = df["event_dt"].apply(lambda d: f"Q{(d.month - 1)//3 + 1} {d.year}")

    df["first_name"] = df.get("first_name", "").fillna("").astype(str).str.strip()
    df["last_name"] = df.get("last_name", "").fillna("").astype(str).str.strip()
    df["mentee_name"] = (df["first_name"] + " " + df["last_name"]).str.strip()
    df.loc[df["mentee_name"] == "", "mentee_name"] = "Unnamed Mentee (" + df["tei"].astype(str).str[:6] + ")"

    df["beneficiary_uid"] = df.apply(_build_beneficiary_uid, axis=1)

    def _extract_county(h):
        parts = [p.strip() for p in str(h or "").split("/") if p.strip()]
        for p in parts:
            if "county" in p.lower():
                return p.replace(" County", "").replace(" county", "").strip()
        return parts[2] if len(parts) > 2 else "Unspecified"

    df["county"] = df.get("ou_hierarchy", "").apply(_extract_county)

    df["modality_code"] = df.get("modality_code", "").fillna("").astype(str).str.strip().str.lower()
    df["Modality"] = df["modality_code"].map(MODALITY_LABELS).fillna("Other / Unspecified")

    g_map = {"FEMALE": "Female", "MALE": "Male", "UNKNOWN": "Unspecified", "": "Unspecified"}
    df["Gender"] = df.get("gender_raw", "").fillna("").astype(str).str.strip().str.upper().map(g_map).fillna("Unspecified")

    def _clean_cadre(val):
        s = str(val or "").strip()
        if not s or s.lower() == "nan":
            return "Unspecified"
        return s.replace("_", " ").title()

    df["Cadre"] = df.get("cadre_raw", "").apply(_clean_cadre)

    classified = df.get("trainer_raw", "").apply(_classify_mentors)
    df["Mentors"] = [c[0] for c in classified]
    df["Mentor_Track"] = [c[1] for c in classified]
    df["Mentor_Cohort"] = [c[2] for c in classified]

    curr_info = [
        _classify_curriculum(m, l, t)
        for m, l, t in zip(df.get("modules", ""), df.get("lessons", ""), df["Mentor_Track"])
    ]
    df["Curriculum"] = [c[0] for c in curr_info]
    df["Modules_Pretty"] = [c[1] for c in curr_info]

    df = df.sort_values(["event_dt", "facility_name", "mentee_name"]).reset_index(drop=True)
    df = df.drop(columns=["event_dt"], errors="ignore")

    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        df.to_csv(MENTEE_SNAPSHOT_PATH, index=False, compression={"method": "gzip", "mtime": 0})
    except Exception:
        pass

    return df
