from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import fitz  # PyMuPDF
import pandas as pd

ACTIVE_STATUSES = {"WKG", "PCF", "RCF", "CF", "95DLC", "D1GLC"}
WORKING_STATUSES = {"WKG"}
SPARE_STATUSES = {"SPR", "SPARE"}
DEFECT_STATUSES = {"DEF"}
REVIEW_STATUSES = {"PCF", "RCF", "CF", "95DLC", "D1GLC", "UNK"}


@dataclass
class ReportMeta:
    file_name: str
    report_type: str
    report_date: str = ""
    work_center: str = ""
    employee: str = ""
    cable_id: str = ""
    pair_low: Optional[int] = None
    pair_high: Optional[int] = None
    page_count: int = 0


def read_pdf_text(file_obj: Any) -> Tuple[str, int]:
    """Return extracted text and page count from path, bytes, or uploaded file."""
    if isinstance(file_obj, (str, Path)):
        doc = fitz.open(str(file_obj))
    else:
        data = file_obj.read() if hasattr(file_obj, "read") else file_obj
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        doc = fitz.open(stream=data, filetype="pdf")
    pages = [page.get_text("text") for page in doc]
    return "\n".join(pages), len(doc)


def detect_report_type(text: str, file_name: str = "") -> str:
    u = (text[:2000] + " " + file_name).upper()
    if "ABBREVIATED CABLE RECORD REPORT" in u or re.search(r"\bACR\b", u):
        return "ACR"
    if "CABLE PAIR OUTPUT" in u:
        if "CAPR" in u:
            return "CAPR/CPR"
        return "CAPR/CPR"
    return "UNKNOWN"


def parse_meta(text: str, file_name: str, page_count: int) -> ReportMeta:
    report_type = detect_report_type(text, file_name)
    # examples: PAIRS 6680P: 1 - 1200, ca MD2010 pr 1 hi 168
    cable_id = ""
    pair_low = pair_high = None
    m = re.search(r"PAIRS\s+([A-Z0-9-]+)\s*:\s*(\d+)\s*-\s*(\d+)", text, re.I)
    if m:
        cable_id, pair_low, pair_high = m.group(1), int(m.group(2)), int(m.group(3))
    else:
        m = re.search(r"\bca\s+([A-Z0-9-]+)\s+pr\s+(\d+)\s+hi\s+(\d+)", text, re.I)
        if m:
            cable_id, pair_low, pair_high = m.group(1), int(m.group(2)), int(m.group(3))
    wc = ""
    emp = ""
    m = re.search(r"\bwc\s+(\d+)\s+emp\s+([A-Z0-9]+)", text, re.I)
    if m:
        wc, emp = m.group(1), m.group(2)
    else:
        m = re.search(r"\bwc\s+(\d+)", text, re.I)
        wc = m.group(1) if m else ""
        m = re.search(r"\bemp\s+([A-Z0-9]+)", text, re.I)
        emp = m.group(1) if m else ""
    report_date = ""
    m = re.search(
        r"\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4}",
        text,
    )
    if m:
        report_date = m.group(0)
    return ReportMeta(
        file_name=file_name,
        report_type=report_type,
        report_date=report_date,
        work_center=wc,
        employee=emp,
        cable_id=cable_id,
        pair_low=pair_low,
        pair_high=pair_high,
        page_count=page_count,
    )


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def parse_pair_records(text: str, meta: ReportMeta) -> List[Dict[str, Any]]:
    """Parse CAPR/CPR pair-level blocks."""
    records: List[Dict[str, Any]] = []
    # Split at lines beginning with "pr <number> stat".
    starts = list(
        re.finditer(r"(?m)^\s*pr\s+(\d+)\s+stat\s+([A-Z0-9]+)\b", text, flags=re.I)
    )
    for i, m in enumerate(starts):
        start = m.start()
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        block = text[start:end]
        pair = int(m.group(1))
        status = m.group(2).upper()
        ckid = ""
        m_ck = re.search(
            r"ckid\s+(.+?)(?:\s+lp\s+stat|\s+bp/clr|\s+tea|\n)",
            block,
            flags=re.I | re.S,
        )
        if m_ck:
            ckid = _clean(m_ck.group(1))
        lp_status = ""
        m_lp = re.search(r"lp\s+stat\s+([A-Z0-9]+)", block, flags=re.I)
        if m_lp:
            lp_status = m_lp.group(1).upper()
        svc_type = ""
        m_svc = re.search(r"svc-typ\s+([A-Z0-9-]+)", block, flags=re.I)
        if m_svc:
            svc_type = m_svc.group(1).upper()
        bp_clr = ""
        m_bp = re.search(r"bp/clr\s+(.+?)(?:\s+tea|\n)", block, flags=re.I | re.S)
        if m_bp:
            bp_clr = _clean(m_bp.group(1))
        capr_ref = ""
        m_capr = re.search(
            r"(?:co side|fld side)\s+capr\s+([A-Z0-9:-]+)", block, flags=re.I
        )
        if m_capr:
            capr_ref = m_capr.group(1)
        address = ""
        m_addr = re.search(
            r"addr:\s+(.+?)(?:\s+com\s+|\s+state\s+|\n)", block, flags=re.I | re.S
        )
        if m_addr:
            address = _clean(m_addr.group(1))
        city = ""
        m_city = re.search(
            r"\bcom\s+([A-Z .-]+?)\s+state\s+([A-Z]{2})\b", block, flags=re.I
        )
        state = ""
        if m_city:
            city = _clean(m_city.group(1)).upper()
            state = m_city.group(2).upper()
        terminal = ""
        m_tea = re.search(
            r"\btea\s+(.+?)\s+type\s+([A-Z0-9]+)", block, flags=re.I | re.S
        )
        if m_tea:
            terminal = _clean(m_tea.group(1))
        defect_type = ""
        m_def = re.search(r"def\s+type\s+([A-Z0-9]+)", block, flags=re.I)
        if m_def:
            defect_type = m_def.group(1).upper()
        record = {
            "source_file": meta.file_name,
            "report_type": meta.report_type,
            "cable_id": meta.cable_id,
            "pair": pair,
            "status": status,
            "status_group": classify_status(status, ckid),
            "ckid": ckid,
            "lp_status": lp_status,
            "svc_type": svc_type,
            "bp_clr": bp_clr,
            "capr_ref": capr_ref,
            "terminal": terminal,
            "address": address,
            "city": city,
            "state": state,
            "defect_type": defect_type,
            "raw_block": _clean(block),
        }
        records.append(record)
    return records


def parse_acr_matrix_rows(text: str, meta: ReportMeta) -> List[Dict[str, Any]]:
    """Parse ACR matrix rows where pair/status appear in compact report lines."""
    rows: List[Dict[str, Any]] = []
    for line in text.splitlines():
        # Example: PCF! ! R! ! 1! *! *! C!
        m = re.search(r"^\s*([A-Z0-9-]*)!.*?!\s*(\d+)!", line)
        if not m:
            continue
        status = m.group(1).strip().upper()
        pair = int(m.group(2))
        if not status:
            # Sometimes status cell is blank; mark unknown rather than inventing a status.
            status = "UNK"
        # Keep only plausible status rows.
        if status in ACTIVE_STATUSES.union(
            SPARE_STATUSES, DEFECT_STATUSES, {"UNK"}
        ) or re.match(r"^(RCF|CF)\d", status):
            normalized = (
                "RCF"
                if status.startswith("RCF")
                else ("CF" if status.startswith("CF") else status)
            )
            rows.append(
                {
                    "source_file": meta.file_name,
                    "report_type": "ACR_MATRIX",
                    "cable_id": meta.cable_id,
                    "pair": pair,
                    "status": normalized,
                    "status_group": classify_status(normalized, ""),
                    "ckid": "",
                    "lp_status": "",
                    "svc_type": "",
                    "bp_clr": "",
                    "capr_ref": "",
                    "terminal": "",
                    "address": "",
                    "city": "",
                    "state": "",
                    "defect_type": "",
                    "raw_block": _clean(line),
                }
            )
    # Avoid duplicates from repeated page headers/pages.
    out = []
    seen = set()
    for r in rows:
        key = (r["source_file"], r["pair"], r["status"], r["raw_block"][:40])
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def classify_status(status: str, ckid: str = "") -> str:
    s = (status or "").upper()
    if s in WORKING_STATUSES or (ckid and ckid.upper() not in {"NONE", "N/A", "NA"}):
        return "Working / active circuit"
    if s in DEFECT_STATUSES:
        return "Defective"
    if s in SPARE_STATUSES:
        return "Spare"
    if s in REVIEW_STATUSES or s.startswith("RCF") or s.startswith("CF"):
        return "Review / assigned"
    return "Unknown / needs check"


def parse_acr_count_sections(text: str, meta: ReportMeta) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    current_terminal = ""
    current_section = ""
    for raw in text.splitlines():
        line = _clean(raw)
        if not line:
            continue
        # Terminal context rows often begin with index and address/type.
        if re.match(r"^(XBOX|\d+\s+|[A-Z0-9]+\s+).*\btype\b", line, re.I):
            if not any(
                key in line.upper()
                for key in ["IN COUNT", "OUT COUNT", "QUALIFIED PAIRS"]
            ):
                current_terminal = line[:180]
        if line.upper().startswith("IN COUNT"):
            current_section = "IN COUNT"
            continue
        if line.upper().startswith("OUT COUNT"):
            current_section = "OUT COUNT"
            continue
        if line.upper().startswith("QUALIFIED PAIRS"):
            current_section = "QUALIFIED PAIRS"
            continue
        if current_section and re.match(r"^(ca|dd|[A-Z0-9]+:)\b", line, re.I):
            m = re.search(r"(?:ca\s+)?([A-Z0-9]+)\s*:?\s*(\d+)\s*-\s*(\d+)", line, re.I)
            rows.append(
                {
                    "source_file": meta.file_name,
                    "cable_id": meta.cable_id,
                    "section": current_section,
                    "terminal_context": current_terminal,
                    "record_text": line,
                    "related_cable": m.group(1).upper() if m else "",
                    "pair_low": int(m.group(2)) if m else None,
                    "pair_high": int(m.group(3)) if m else None,
                }
            )
    return rows


def analyze_files(
    files: Iterable[Any], names: Optional[Iterable[str]] = None
) -> Dict[str, Any]:
    metas: List[ReportMeta] = []
    pair_rows: List[Dict[str, Any]] = []
    count_rows: List[Dict[str, Any]] = []
    if names is None:
        names = [getattr(f, "name", str(f)) for f in files]
    for f, name in zip(files, names):
        text, pages = read_pdf_text(f)
        meta = parse_meta(text, Path(str(name)).name, pages)
        metas.append(meta)
        if meta.report_type == "ACR":
            pair_rows.extend(parse_acr_matrix_rows(text, meta))
            count_rows.extend(parse_acr_count_sections(text, meta))
        elif meta.report_type == "CAPR/CPR":
            pair_rows.extend(parse_pair_records(text, meta))
        else:
            # Try both, but mark unknown source report type.
            pair_rows.extend(parse_pair_records(text, meta))
            count_rows.extend(parse_acr_count_sections(text, meta))
    pair_df = pd.DataFrame(pair_rows)
    count_df = pd.DataFrame(count_rows)
    meta_df = pd.DataFrame([asdict(m) for m in metas])
    summary = build_summary(pair_df, count_df, meta_df)
    return {"meta": meta_df, "pairs": pair_df, "counts": count_df, "summary": summary}


def build_summary(
    pair_df: pd.DataFrame, count_df: pd.DataFrame, meta_df: pd.DataFrame
) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "files_processed": int(len(meta_df)),
        "total_pair_records": int(len(pair_df)),
        "acr_count_records": int(len(count_df)),
        "cables": sorted(
            [
                str(x)
                for x in meta_df.get("cable_id", pd.Series(dtype=str)).dropna().unique()
                if str(x)
            ]
        ),
        "decision": "NO DATA",
        "decision_reason": "Upload ACR/CAPR/CPR PDFs to generate a decision.",
        "status_counts": {},
        "status_group_counts": {},
    }
    if not pair_df.empty:
        summary["status_counts"] = (
            pair_df["status"].value_counts(dropna=False).to_dict()
        )
        summary["status_group_counts"] = (
            pair_df["status_group"].value_counts(dropna=False).to_dict()
        )
        working = int((pair_df["status_group"] == "Working / active circuit").sum())
        review = int((pair_df["status_group"] == "Review / assigned").sum())
        defective = int((pair_df["status_group"] == "Defective").sum())
        spare = int((pair_df["status_group"] == "Spare").sum())
        summary.update(
            {
                "working_active_records": working,
                "review_assigned_records": review,
                "defective_records": defective,
                "spare_records": spare,
            }
        )
        if working > 0:
            summary["decision"] = "HOLD / DO NOT DECOM YET"
            summary["decision_reason"] = (
                f"{working} working/active circuit record(s) were found. Validate customer/billing/disconnect before removal."
            )
        elif review > 0:
            summary["decision"] = "ENGINEERING REVIEW REQUIRED"
            summary["decision_reason"] = (
                f"{review} assigned/review record(s) were found. Verify ACR/CAPR routing and customer status."
            )
        else:
            summary["decision"] = "PROCEED CANDIDATE"
            summary["decision_reason"] = (
                "No working/active pair records were found in the uploaded files. Final field and billing validation still required."
            )
    return summary


def export_summary_json(summary: Dict[str, Any]) -> str:
    return json.dumps(summary, indent=2, default=str)
