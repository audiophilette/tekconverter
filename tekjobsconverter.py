#!/usr/bin/env python3
## 2026-02-12 "CJG <audiophilette@protonmail.com>"

import argparse
import os
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
import pandas as pd

def extract_html_from_mhtml(path):
    with open(path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    for part in msg.walk():
        if part.get_content_type() == "text/html":
            return part.get_content()

    raise ValueError("No text/html part found in MHTML file")


def main():
    parser = argparse.ArgumentParser(
        description="Convert MHTML file tables to CSV"
    )
    parser.add_argument("input", help="Path to MHTML file")
    parser.add_argument(
        "-o", "--output",
        help="Output CSV filename (default: combined_output.csv)",
        default="combined_output.csv"
    )
    parser.add_argument(
        "--table-index",
        type=int,
        help="Specific table index to export (default: all combined)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug info about detected tables"
    )

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        raise FileNotFoundError(f"File not found: {args.input}")

    html_content = extract_html_from_mhtml(args.input)
    soup = BeautifulSoup(html_content, "lxml")

    from io import StringIO

    tables = pd.read_html(StringIO(str(soup)))

    if args.debug:
        print(f"Detected {len(tables)} table(s)")
        for i, t in enumerate(tables):
            print(f"Table {i} shape: {t.shape}")

    if not tables:
        raise ValueError("No HTML <table> elements found.")

    if args.table_index is not None:
        if args.table_index >= len(tables):
            raise IndexError("Table index out of range.")
        df = tables[args.table_index]
    else:
        df = pd.concat(tables, ignore_index=True)

    df.to_csv(args.output, index=False)
    print(f"Saved CSV to {args.output}")


if __name__ == "__main__":
    main()
