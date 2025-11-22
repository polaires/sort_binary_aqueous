#!/usr/bin/env python3
"""
PDF Page Filter - Extract specific pages from a PDF based on printed page numbers.

This script reads the actual page numbers printed on each page (e.g., in the
top corners) and filters based on those numbers, not the physical page position.
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


def extract_page_number_from_text(text):
    """
    Extract page number from text (usually from top of page).

    Args:
        text: Text extracted from the page

    Returns:
        Page number as integer, or None if not found
    """
    if not text:
        return None

    # Take only first few lines (top of page)
    lines = text.strip().split('\n')[:5]
    top_text = '\n'.join(lines)

    # Look for standalone numbers (common page number patterns)
    # Pattern 1: Just a number on its own line or with minimal text
    patterns = [
        r'^\s*(\d+)\s*$',                    # Just a number
        r'^\s*-?\s*(\d+)\s*-?\s*$',          # Number with dashes (- 5 -)
        r'^\s*Page\s+(\d+)',                 # "Page 5"
        r'^\s*P\.?\s*(\d+)',                 # "P. 5" or "P 5"
        r'(?:^|\s)(\d{1,4})(?:\s|$)',        # Standalone 1-4 digit number
    ]

    for line in lines:
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                page_num = int(match.group(1))
                # Reasonable page number (1-9999)
                if 1 <= page_num <= 9999:
                    return page_num

    return None


def detect_page_numbers(reader, verbose=True):
    """
    Detect printed page numbers on each page of the PDF.

    Args:
        reader: PdfReader object
        verbose: Print progress information

    Returns:
        Dictionary mapping physical page index (0-indexed) to printed page number
    """
    page_mapping = {}
    total_pages = len(reader.pages)

    if verbose:
        print("\nDetecting page numbers printed on pages...")
        print("-" * 60)

    for physical_idx in range(total_pages):
        try:
            page = reader.pages[physical_idx]
            text = page.extract_text()

            # Extract page number from top of page
            printed_num = extract_page_number_from_text(text)

            if printed_num:
                page_mapping[physical_idx] = printed_num
                if verbose:
                    print(f"Physical page {physical_idx + 1:3d} -> Printed page number: {printed_num}")
            else:
                if verbose:
                    print(f"Physical page {physical_idx + 1:3d} -> No page number detected")

        except Exception as e:
            if verbose:
                print(f"Physical page {physical_idx + 1:3d} -> Error extracting text: {e}")

    if verbose:
        print("-" * 60)
        print(f"Detected page numbers on {len(page_mapping)}/{total_pages} pages\n")

    return page_mapping


def interpolate_missing_pages(page_mapping, total_pages, verbose=True):
    """
    Intelligently fill in missing page numbers based on detected sequences.

    Args:
        page_mapping: Dictionary of physical index -> printed page number
        total_pages: Total number of physical pages
        verbose: Print interpolation information

    Returns:
        Updated page_mapping with interpolated values
    """
    if not page_mapping:
        return page_mapping

    interpolated = page_mapping.copy()

    if verbose:
        print("Interpolating missing page numbers...")
        print("-" * 60)

    # Find sequences of consecutive detected pages
    detected_indices = sorted(page_mapping.keys())

    # Look for patterns and fill gaps
    for i in range(len(detected_indices) - 1):
        phys_start = detected_indices[i]
        phys_end = detected_indices[i + 1]

        page_start = page_mapping[phys_start]
        page_end = page_mapping[phys_end]

        # Calculate the gap
        phys_gap = phys_end - phys_start
        page_gap = page_end - page_start

        # If the gaps match or are close, interpolate
        # Allow for some flexibility (e.g., one skipped page number)
        if phys_gap > 1 and phys_gap <= 10 and page_gap >= phys_gap - 2 and page_gap <= phys_gap + 2:
            # Linear interpolation
            if page_gap == phys_gap:
                # Perfect match - sequential numbering
                for j in range(1, phys_gap):
                    phys_idx = phys_start + j
                    inferred_page = page_start + j
                    if phys_idx not in interpolated:
                        interpolated[phys_idx] = inferred_page
                        if verbose:
                            print(f"Physical page {phys_idx + 1:3d} -> Inferred page number: {inferred_page}")
            elif page_gap == phys_gap - 1:
                # One physical page doesn't have a number (likely blank/separator)
                # Fill in the sequential ones
                current_page = page_start
                for j in range(1, phys_gap):
                    phys_idx = phys_start + j
                    if phys_idx not in interpolated:
                        # Try to infer if this should be numbered or blank
                        expected_page = current_page + 1
                        if expected_page < page_end:
                            interpolated[phys_idx] = expected_page
                            current_page = expected_page
                            if verbose:
                                print(f"Physical page {phys_idx + 1:3d} -> Inferred page number: {expected_page}")
                        else:
                            if verbose:
                                print(f"Physical page {phys_idx + 1:3d} -> Likely unnumbered page (blank/separator)")

    # Handle pages before the first detected page
    if detected_indices:
        first_detected = detected_indices[0]
        first_page_num = page_mapping[first_detected]

        # If first detected page has a reasonable page number, backfill
        if first_page_num > 1 and first_page_num - 1 <= first_detected:
            for phys_idx in range(first_detected - 1, -1, -1):
                inferred_page = first_page_num - (first_detected - phys_idx)
                if inferred_page >= 1 and phys_idx not in interpolated:
                    interpolated[phys_idx] = inferred_page
                    if verbose:
                        print(f"Physical page {phys_idx + 1:3d} -> Inferred page number: {inferred_page} (backfilled)")
                else:
                    break

    # Handle pages after the last detected page
    if detected_indices:
        last_detected = detected_indices[-1]
        last_page_num = page_mapping[last_detected]

        # Look for a consistent increment pattern near the end
        if len(detected_indices) >= 2:
            # Check if we have a consistent pattern
            prev_detected = detected_indices[-2]
            if last_detected - prev_detected == 1:
                # Sequential physical pages, extend forward
                for phys_idx in range(last_detected + 1, total_pages):
                    inferred_page = last_page_num + (phys_idx - last_detected)
                    if phys_idx not in interpolated:
                        interpolated[phys_idx] = inferred_page
                        if verbose:
                            print(f"Physical page {phys_idx + 1:3d} -> Inferred page number: {inferred_page} (forward fill)")

    if verbose:
        print("-" * 60)
        added_count = len(interpolated) - len(page_mapping)
        print(f"Interpolated {added_count} additional page numbers")
        print(f"Total pages mapped: {len(interpolated)}/{total_pages}\n")

    return interpolated


def parse_page_ranges(range_string):
    """
    Parse page range string like "1-3, 5, 7-10" into a list of page numbers.

    Args:
        range_string: String containing page ranges

    Returns:
        Sorted list of unique page numbers
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


def filter_pdf_pages(input_path, output_path, page_ranges, use_printed_numbers=True):
    """
    Extract specific pages from a PDF and create a new PDF.

    Args:
        input_path: Path to input PDF file
        output_path: Path to output PDF file
        page_ranges: String of page ranges (e.g., "1-3, 5, 7-10")
        use_printed_numbers: If True, use printed page numbers; if False, use physical position
    """
    # Parse page ranges
    requested_pages = parse_page_ranges(page_ranges)

    if not requested_pages:
        print("Error: No valid pages specified")
        return False

    print(f"Requested page numbers: {requested_pages}")

    # Read input PDF
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        print(f"Input PDF has {total_pages} physical pages\n")

        if use_printed_numbers:
            # Detect printed page numbers
            page_mapping = detect_page_numbers(reader, verbose=True)

            if not page_mapping:
                print("\nWarning: No page numbers detected on any pages!")
                print("Falling back to physical page numbers...")
                use_printed_numbers = False
            else:
                # Interpolate missing page numbers
                page_mapping = interpolate_missing_pages(page_mapping, total_pages, verbose=True)

        # Create output PDF
        writer = PdfWriter()
        pages_added = []

        if use_printed_numbers and page_mapping:
            # Filter by printed page numbers
            print("Filtering by printed page numbers...")

            # Create reverse mapping: printed number -> physical indices
            printed_to_physical = {}
            for phys_idx, printed_num in page_mapping.items():
                if printed_num not in printed_to_physical:
                    printed_to_physical[printed_num] = []
                printed_to_physical[printed_num].append(phys_idx)

            # Add pages with matching printed numbers
            for printed_num in requested_pages:
                if printed_num in printed_to_physical:
                    for phys_idx in printed_to_physical[printed_num]:
                        writer.add_page(reader.pages[phys_idx])
                        pages_added.append(printed_num)
                        print(f"Added page with printed number {printed_num} (physical page {phys_idx + 1})")
                else:
                    print(f"Warning: No page found with printed number {printed_num}")
        else:
            # Filter by physical page numbers
            print("Filtering by physical page numbers...")

            for page_num in requested_pages:
                if 1 <= page_num <= total_pages:
                    writer.add_page(reader.pages[page_num - 1])
                    pages_added.append(page_num)
                    print(f"Added physical page {page_num}")
                else:
                    print(f"Warning: Physical page {page_num} is out of range (1-{total_pages})")

        if not pages_added:
            print("\nError: No pages were added to output PDF")
            return False

        # Write output file
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        print(f"\nSuccess! Created '{output_path}' with {len(pages_added)} pages")
        return True

    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found")
        return False
    except Exception as e:
        print(f"Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to run the PDF page filter."""
    print("=" * 60)
    print("PDF Page Filter (Smart Page Number Detection)")
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
        print("\nEnter page numbers to keep (e.g., '2-5, 17-20, 25'):")
        print("(This will look for these numbers printed on the pages)")
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
    success = filter_pdf_pages(input_path, output_path, page_ranges, use_printed_numbers=True)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
