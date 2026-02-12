import argparse
import pandas as pd
import sys
import os

def extract_headers(excel_file, sheet):
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet)
        return df.columns.tolist()
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Extract column headers (first row) from an Excel file"
    )
    parser.add_argument(
        "file",
        help="Path to the Excel file (.xlsx)"
    )
    parser.add_argument(
        "-s", "--sheet",
        default=0,
        help="Sheet name or index (default: first sheet)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
        sys.exit(1)

    headers = extract_headers(args.file, args.sheet)

    print("\nExtracted attributes (headers):")
    for header in headers:
        print(header)


if __name__ == "__main__":
    main()
