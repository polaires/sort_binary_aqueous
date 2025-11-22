# PDF Page Filter

A Python script to extract specific pages from PDF files based on **printed page numbers**, not physical page positions.

## Features

- **Smart page number detection** - Reads actual page numbers printed on pages (top corners)
- Filters by printed page numbers, not physical page position
- Support for page ranges (e.g., "2-5, 17-20")
- Support for individual pages (e.g., "1, 3, 5")
- Interactive or command-line usage
- Automatic fallback to physical page numbers if printed numbers can't be detected
- Shows detailed mapping of physical pages to printed page numbers

## Installation

1. Install Python 3.6 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install PyPDF2
```

## Usage

### Interactive Mode

Run the script without arguments for interactive prompts:

```bash
python pdf_page_filter.py
```

The script will:
1. Ask for input PDF path
2. Scan the PDF and detect printed page numbers on each page
3. Ask for page numbers to keep (e.g., "2-5, 17-20, 25")
4. Ask for output PDF path
5. Extract pages with matching printed numbers

### Command-Line Mode

```bash
python pdf_page_filter.py <input.pdf> <page_ranges> [output.pdf]
```

**Examples:**

```bash
# Extract pages with PRINTED numbers 2-5 and 17-20
python pdf_page_filter.py SDS-61.pdf "2-5, 17-20"

# Extract pages with PRINTED numbers 1, 3, 5, and 10-15
python pdf_page_filter.py SDS-61.pdf "1, 3, 5, 10-15" output.pdf

# Extract single page with PRINTED number 7
python pdf_page_filter.py document.pdf "7"
```

## How It Works

The script automatically detects page numbers printed on each page by:
1. Extracting text from the top portion of each page
2. Looking for common page number patterns (standalone numbers, "Page X", etc.)
3. Creating a mapping between physical page positions and printed page numbers
4. Filtering pages based on their printed numbers, not their physical position

**Important**: The script uses **printed page numbers** (the numbers you see on the page), not the physical page position in the PDF file.

## Page Range Format

The script accepts page ranges in the following formats:

- **Individual pages**: `1, 3, 5` (printed page numbers)
- **Page ranges**: `2-5` (includes printed pages 2, 3, 4, 5)
- **Mixed**: `1-3, 5, 7-10, 15`

**Note**: Numbers refer to the page numbers **printed on the pages**, not their physical position in the PDF.

## Example Output

```bash
$ python pdf_page_filter.py SDS-61.pdf "1-3"
============================================================
PDF Page Filter (Smart Page Number Detection)
============================================================

Requested page numbers: [1, 2, 3]
Input PDF has 286 physical pages

Detecting page numbers printed on pages...
------------------------------------------------------------
Physical page   1 -> No page number detected
Physical page   2 -> No page number detected
...
Physical page  15 -> Printed page number: 1
...
Physical page  20 -> Printed page number: 2
...
------------------------------------------------------------
Detected page numbers on 169/286 pages

Filtering by printed page numbers...
Added page with printed number 1 (physical page 15)
Added page with printed number 2 (physical page 20)
Warning: No page found with printed number 3

Success! Created 'SDS-61_filtered.pdf' with 2 pages
```

The script shows you exactly which physical pages contain which printed page numbers, making it easy to verify the correct pages are being extracted.

## Requirements

- Python 3.6+
- PyPDF2 3.0.0+