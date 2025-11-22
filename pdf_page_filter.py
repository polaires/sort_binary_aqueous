#!/usr/bin/env python3
"""
PDF Page Filter - Extract specific pages from a PDF based on page ranges.

This script allows you to filter PDF pages by specifying page ranges
(e.g., "2-5, 17-20") and creates a new PDF with only those pages.
"""

import sys
import re
from pathlib import Path

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("Error: PDF library not found.")
        print("Please install using: pip install PyPDF2")
        print("Or alternatively: pip install pypdf")
        sys.exit(1)


def parse_page_ranges(range_string):
    """
    Parse page range string like "1-3, 5, 7-10" into a list of page numbers.

    Args:
        range_string: String containing page ranges

    Returns:
        Sorted list of unique page numbers (1-indexed)
    """
    pages = set()

    # Split by comma and process each part
    parts = [part.strip() for part in range_string.split(',')]

    for part in parts:
        if not part:
            continue

        # Check if it's a range (e.g., "5-10")
        if '-' in part:
            try:
                start, end = part.split('-', 1)
                start = int(start.strip())
                end = int(end.strip())

                if start > end:
                    print(f"Warning: Invalid range {start}-{end}, skipping")
                    continue

                pages.update(range(start, end + 1))
            except ValueError:
                print(f"Warning: Invalid range format '{part}', skipping")
                continue
        else:
            # Single page number
            try:
                pages.add(int(part))
            except ValueError:
                print(f"Warning: Invalid page number '{part}', skipping")
                continue

    return sorted(list(pages))


def filter_pdf_pages(input_path, output_path, page_ranges):
    """
    Extract specific pages from a PDF and create a new PDF.

    Args:
        input_path: Path to input PDF file
        output_path: Path to output PDF file
        page_ranges: String of page ranges (e.g., "1-3, 5, 7-10")
    """
    # Parse page ranges
    pages_to_keep = parse_page_ranges(page_ranges)

    if not pages_to_keep:
        print("Error: No valid pages specified")
        return False

    print(f"Pages to extract: {pages_to_keep}")

    # Read input PDF
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        print(f"Input PDF has {total_pages} pages")

        # Validate page numbers
        invalid_pages = [p for p in pages_to_keep if p < 1 or p > total_pages]
        if invalid_pages:
            print(f"Warning: These pages are out of range and will be skipped: {invalid_pages}")
            pages_to_keep = [p for p in pages_to_keep if 1 <= p <= total_pages]

        if not pages_to_keep:
            print("Error: No valid pages to extract")
            return False

        # Create output PDF
        writer = PdfWriter()

        # Add selected pages (convert from 1-indexed to 0-indexed)
        for page_num in pages_to_keep:
            writer.add_page(reader.pages[page_num - 1])
            print(f"Added page {page_num}")

        # Write output file
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        print(f"\nSuccess! Created '{output_path}' with {len(pages_to_keep)} pages")
        return True

    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found")
        return False
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False


def main():
    """Main function to run the PDF page filter."""
    print("=" * 60)
    print("PDF Page Filter")
    print("=" * 60)

    # Get input PDF path
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = input("Enter input PDF path: ").strip()

    if not input_path:
        print("Error: No input file specified")
        sys.exit(1)

    input_path = Path(input_path)

    if not input_path.exists():
        print(f"Error: File '{input_path}' does not exist")
        sys.exit(1)

    # Get page ranges
    if len(sys.argv) > 2:
        page_ranges = sys.argv[2]
    else:
        print("\nEnter page ranges to keep (e.g., '2-5, 17-20, 25'):")
        page_ranges = input("> ").strip()

    if not page_ranges:
        print("Error: No page ranges specified")
        sys.exit(1)

    # Get output path
    if len(sys.argv) > 3:
        output_path = sys.argv[3]
    else:
        default_output = input_path.stem + "_filtered.pdf"
        output_input = input(f"Enter output PDF path (default: {default_output}): ").strip()
        output_path = output_input if output_input else default_output

    output_path = Path(output_path)

    # Confirm if output file exists
    if output_path.exists():
        confirm = input(f"Output file '{output_path}' exists. Overwrite? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled")
            sys.exit(0)

    print()

    # Process PDF
    success = filter_pdf_pages(input_path, output_path, page_ranges)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
