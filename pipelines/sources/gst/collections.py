"""GST gross and net collections, monthly, from the GST portal's statistics workbook.

File: https://tutorial.gst.gov.in/offlineutilities/gst_statistics/Gross_Net_Tax_collection.xlsx
(linked from https://www.gst.gov.in/download/gststatistics). One sheet per month
(Apr-24 onwards); in each, column B is the same month a year earlier and column C the
month itself, in ₹ crore. Rows are found by label because the layout changes (cess rows
disappear in later sheets).

The sheet name gives the month; a sheet whose column-C header disagrees is skipped.
Levels come only from each month's own sheet (column C). The year-earlier column may be
restated on a later definition, so growth is computed within one sheet (C/B - 1), which
keeps both sides on the same definition. Stored in ₹ lakh crore.
"""
from __future__ import annotations

import io
import re
from datetime import datetime

import pandas as pd

from pipelines.core import Raw, Source
from pipelines.core.http import fetch_raw

URL = "https://tutorial.gst.gov.in/offlineutilities/gst_statistics/Gross_Net_Tax_collection.xlsx"
LEVELS = {"Total Gross GST Revenue": "gst_gross_collections",
          "Total Net GST Revenue": "gst_net_collections", "Total Refund": "gst_refunds"}
GROWTH = {"Total Gross GST Revenue": "gst_gross_growth", "Total Net GST Revenue": "gst_net_growth"}


def month_of(header) -> str:
    """Column header -> ISO first-of-month. Seen: datetimes, 'Aug-26', 'Mar_26', 'June 24'."""
    if isinstance(header, datetime):
        return header.strftime("%Y-%m-01")
    m = re.match(r"\s*([A-Za-z]{3})[A-Za-z]*[\s\-_']*(\d{2}|\d{4})\s*$", str(header))
    if not m:
        raise ValueError(f"unrecognised month header {header!r}")
    year = int(m.group(2)) + (2000 if len(m.group(2)) == 2 else 0)
    return datetime.strptime(f"{m.group(1).title()} {year}", "%b %Y").strftime("%Y-%m-01")


class GstCollections(Source):
    name = "gst_collections"
    series_ids = (*LEVELS.values(), *GROWTH.values())

    def fetch(self) -> list[Raw]:
        return [fetch_raw(URL, suffix=".xlsx")]

    def parse(self, raws: list[Raw]) -> pd.DataFrame:
        book = pd.read_excel(io.BytesIO(raws[0].content), sheet_name=None, header=None)
        rows = []
        for name, df in book.items():
            header = df.index[df[0].astype(str).str.strip() == "GST Collections"]
            if not len(header):
                raise ValueError(f"sheet {name!r}: no 'GST Collections' header row")
            period = month_of(name)
            if month_of(df.iloc[header[0], 2]) != period:
                # The sheet's own header disagrees with its name (seen for Jan-25, whose
                # columns are shifted in the source). Skip it rather than guess.
                print(f"  GST: sheet {name!r} header {df.iloc[header[0], 2]!r} does not match; skipped")
                continue
            labels = df[0].astype(str).str.strip()
            for label, sid in LEVELS.items():
                hit = df[labels == label]
                if hit.empty:
                    raise ValueError(f"sheet {name!r}: row {label!r} missing")
                prev, cur = float(hit.iloc[0, 1]), float(hit.iloc[0, 2])
                rows.append({"series_id": sid, "period": period, "value": round(cur / 1e5, 4)})
                if label in GROWTH:
                    rows.append({"series_id": GROWTH[label], "period": period,
                                 "value": round((cur / prev - 1) * 100, 2)})
        out = pd.DataFrame(rows)
        out["note"] = "provisional (GST portal)"
        return out


SOURCE = GstCollections()
