---
name: pdf
name_zh: pdf
description: Use when tasks involve reading, creating, or reviewing PDF files 
  where rendering and layout matter; prefer visual checks by rendering pages 
  (Poppler) and use Python tools such as `reportlab`, `pdfplumber`, and `pypdf` 
  for generation and extraction.
description_zh: Use when tasks involve reading, creating, or reviewing PDF files
  where rendering and layout matter; prefer visual checks by rendering pages 
  (Poppler) and use Python tools such as `reportlab`, `pdfplumber`, and `pypdf` 
  for generation and extraction.
category: dev-tools
tags:
  - ai
  - cli
  - documentation
  - frontend
  - python
needs_review: false
source:
slug: pdf
version: 1.0.0
created: '2026-06-12'
updated: '2026-06-12'
inputs:
  - name: request
    type: string
    required: true
    description: User request or task description
output:
  format: markdown
  description: Generated content based on the user request
author: AI-SKILL
license: MIT
---
# When to use

Use this skill when tasks involve reading or reviewing PDF content where layout and visuals matter, creating PDFs programmatically with reliable formatting, or validating final rendering before delivery. Prefer visual checks by rendering pages with Poppler (`pdftoppm`) and use Python tools such as `reportlab`, `pdfplumber`, and `pypdf` for generation and extraction.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# PDF Skill

## When to use
- Read or review PDF content where layout and visuals matter.
- Create PDFs programmatically with reliable formatting.
- Validate final rendering before delivery.

## Workflow
1. Prefer visual review: render PDF pages to PNGs and inspect them.
   - Use `pdftoppm` if available.
   - If unavailable, install Poppler or ask the user to review the output locally.
2. Use `reportlab` to generate PDFs when creating new documents.
3. Use `pdfplumber` (or `pypdf`) for text extraction and quick checks; do not rely on it for layout fidelity.
4. After each meaningful update, re-render pages and verify alignment, spacing, and legibility.

## Temp and output conventions
- Use `tmp/pdfs/` for intermediate files; delete when done.
- Write final artifacts under `output/pdf/` when working in this repo.
- Keep filenames stable and descriptive.

## Dependencies (install if missing)
Prefer `uv` for dependency management.

Python packages:
```
uv pip install reportlab pdfplumber pypdf
```
If `uv` is unavailable:
```
python3 -m pip install reportlab pdfplumber pypdf
```
System tools (for rendering):
```
# macOS (Homebrew)
brew install poppler

# Ubuntu/Debian
sudo apt-get install -y poppler-utils
```

If installation isn't possible in this environment, tell the user which dependency is missing and how to install it locally.

## Environment
No required environment variables.

## Rendering command
```
pdftoppm -png $INPUT_PDF $OUTPUT_PREFIX
```

## Quality expectations
- Maintain polished visual design: consistent typography, spacing, margins, and section hierarchy.
- Avoid rendering issues: clipped text, overlapping elements, broken tables, black squares, or unreadable glyphs.
- Charts, tables, and images must be sharp, aligned, and clearly labeled.
- Use ASCII hyphens only. Avoid U+2011 (non-breaking hyphen) and other Unicode dashes.
- Citations and references must be human-readable; never leave tool tokens or placeholder strings.

## Final checks
- Do not deliver until the latest PNG inspection shows zero visual or formatting defects.
- Confirm headers/footers, page numbering, and section transitions look polished.
- Keep intermediate files organized or remove them after final approval.

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

Creating a PDF report with reportlab and verifying the output:

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import subprocess
from pathlib import Path

# Setup
output_dir = Path("tmp/pdfs")
output_dir.mkdir(parents=True, exist_ok=True)
pdf_path = output_dir / "quarterly-report.pdf"

# Create PDF
doc = SimpleDocTemplate(
    str(pdf_path),
    pagesize=letter,
    rightMargin=72,
    leftMargin=72,
    topMargin=72,
    bottomMargin=72
)

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    alignment=TA_CENTER,
    spaceAfter=30
)

# Build content
story = []
story.append(Paragraph("Q2 2026 Performance Report", title_style))
story.append(Spacer(1, 0.25 * inch))

# Add summary paragraph
summary = """
This quarter we achieved 115% of our target revenue, with strong growth 
in the enterprise segment. Customer acquisition costs decreased by 12% 
while retention rates improved to 94%.
"""
story.append(Paragraph(summary, styles['Normal']))
story.append(Spacer(1, 0.3 * inch))

# Add metrics table
data = [
    ['Metric', 'Q1 2026', 'Q2 2026', 'Change'],
    ['Revenue', '$2.1M', '$2.4M', '+14%'],
    ['Customers', '1,234', '1,456', '+18%'],
    ['Churn Rate', '8.2%', '6.1%', '-2.1pp'],
    ['NPS Score', '42', '58', '+16']
]

table = Table(data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))

story.append(table)

# Generate PDF
doc.build(story)
print(f"PDF created: {pdf_path}")

# Verify rendering with pdftoppm
png_prefix = output_dir / "report-page"
subprocess.run([
    "pdftoppm", "-png", "-r", "150",
    str(pdf_path),
    str(png_prefix)
], check=True)

# List generated PNGs for visual inspection
for png in output_dir.glob("report-page-*.png"):
    print(f"Rendered page: {png}")
    # Manually inspect the PNG to verify layout, alignment, and readability
```

Extracting text from an existing PDF:

```python
import pdfplumber
from pathlib import Path

pdf_path = Path("input/document.pdf")

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f"--- Page {i+1} ---")
        print(text)
        
        # Extract tables if present
        tables = page.extract_tables()
        if tables:
            print(f"\nFound {len(tables)} table(s):")
            for j, table in enumerate(tables):
                print(f"Table {j+1}:")
                for row in table:
                    print(row)
```
