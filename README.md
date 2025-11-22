# PDF Page Filter

A Python script to extract specific pages from PDF files based on page ranges.

## Features

- Extract specific pages from PDF files
- Support for page ranges (e.g., "2-5, 17-20")
- Support for individual pages (e.g., "1, 3, 5")
- Interactive or command-line usage
- Creates filtered PDF with only selected pages

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

The script will ask you for:
1. Input PDF path
2. Page ranges to keep (e.g., "2-5, 17-20, 25")
3. Output PDF path

### Command-Line Mode

```bash
python pdf_page_filter.py <input.pdf> <page_ranges> [output.pdf]
```

**Examples:**

```bash
# Extract pages 2-5 and 17-20
python pdf_page_filter.py SDS-61.pdf "2-5, 17-20"

# Extract pages 1, 3, 5, and 10-15
python pdf_page_filter.py SDS-61.pdf "1, 3, 5, 10-15" output.pdf

# Extract single page
python pdf_page_filter.py document.pdf "7"
```

## Page Range Format

The script accepts page ranges in the following formats:

- **Individual pages**: `1, 3, 5`
- **Page ranges**: `2-5` (includes pages 2, 3, 4, 5)
- **Mixed**: `1-3, 5, 7-10, 15`

**Note**: Page numbers are 1-indexed (first page is page 1).

## Example

```bash
# Extract pages 2-5 and 17-20 from SDS-61.pdf
python pdf_page_filter.py SDS-61.pdf "2-5, 17-20"

# Output will be: SDS-61_filtered.pdf
```

## Requirements

- Python 3.6+
- PyPDF2 3.0.0+