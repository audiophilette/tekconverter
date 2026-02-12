cat #!/usr/bin/env python3

import argparse
import os
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
import pandas as pd
import requests
from io import StringIO


def extract_html_from_mhtml(path):
    with open(path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    for part in msg.walk():
        if part.get_content_type() == "text/html":
            return part.get_content()

    raise ValueError("No text/html part found in MHTML file")


def fetch_html_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.text


def main():
    parser = argparse.ArgumentParser(
        description="Convert MHTML or webpage tables to CSV"
    )
    parser.add_argument("source", help="Path to MHTML file OR URL")
    parser.add_argument(
        "-o", "--output",
        default="output.csv",
        help="Output CSV filename"
    )
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    # Decide whether source is URL or file
    if args.source.startswith("http"):
        html_content = fetch_html_from_url(args.source)
    else:
        if not os.path.isfile(args.source):
            raise FileNotFoundError(f"File not found: {args.source}")
        html_content = extract_html_from_mhtml(args.source)

    soup = BeautifulSoup(html_content, "lxml")

    tables = pd.read_html(StringIO(str(soup)))

    if args.debug:
        print(f"Detected {len(tables)} table(s)")
        for i, t in enumerate(tables):
            print(f"Table {i} shape: {t.shape}")

    if not tables:
        raise ValueError("No HTML <table> elements found.")

    df = pd.concat(tables, ignore_index=True)
    df.to_csv(args.output, index=False)

    print(f"Saved CSV to {args.output}")


if __name__ == "__main__":
    main()
