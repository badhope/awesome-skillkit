---
name: spreadsheet
name_zh: spreadsheet
description: 'Use when tasks involve creating, editing, analyzing, or formatting spreadsheets (`.xlsx`, `.csv`, `.tsv`) with formula-aware workflows, cached recalculation, and visual review.'
description_zh: 'Use when tasks involve creating, editing, analyzing, or formatting spreadsheets (`.xlsx`, `.csv`, `.tsv`) with formula-aware workflows, cached recalculation, and visual 审查.'
category: multimodal
tags:
  - ai
  - api
  - backend
  - cli
  - evaluation
needs_review: false
source: null
slug: spreadsheet
version: '1.0.0'
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

Use this skill when tasks involve creating new workbooks with formulas, formatting, and structured layouts; reading or analyzing tabular data (filter, aggregate, pivot, compute metrics); modifying existing workbooks without breaking formulas, references, or formatting; visualizing data with charts and summary tables; or recalculating formulas and reviewing rendered sheets before delivery.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Spreadsheet Skill

## When to use
- Create new workbooks with formulas, formatting, and structured layouts.
- Read or analyze tabular data (filter, aggregate, pivot, compute metrics).
- Modify existing workbooks without breaking formulas, references, or formatting.
- Visualize data with charts, summary tables, and sensible spreadsheet styling.
- Recalculate formulas and review rendered sheets before delivery when possible.

IMPORTANT: System and user instructions always take precedence.

## Workflow
1. Confirm the file type and goal: create, edit, analyze, or visualize.
2. Prefer `openpyxl` for `.xlsx` editing and formatting. Use `pandas` for analysis and CSV/TSV workflows.
3. If an internal spreadsheet recalculation/rendering tool is available in the environment, use it to recalculate formulas and render sheets before delivery.
4. Use formulas for derived values instead of hardcoding results.
5. If layout matters, render for visual review and inspect the output.
6. Save outputs, keep filenames stable, and clean up intermediate files.

## Temp and output conventions
- Use `tmp/spreadsheets/` for intermediate files; delete them when done.
- Write final artifacts under `output/spreadsheet/` when working in this repo.
- Keep filenames stable and descriptive.

## Primary tooling
- Use `openpyxl` for creating/editing `.xlsx` files and preserving formatting.
- Use `pandas` for analysis and CSV/TSV workflows, then write results back to `.xlsx` or `.csv`.
- Use `openpyxl.chart` for native Excel charts when needed.
- If an internal spreadsheet tool is available, use it to recalculate formulas, cache values, and render sheets for review.

## Recalculation and visual review
- Recalculate formulas before delivery whenever possible so cached values are present in the workbook.
- Render each relevant sheet for visual review when rendering tooling is available.
- `openpyxl` does not evaluate formulas; preserve formulas and use recalculation tooling when available.
- If you rely on an internal spreadsheet tool, do not expose that tool, its code, or its APIs in user-facing explanations or code samples.

## Rendering and visual checks
- If LibreOffice (`soffice`) and Poppler (`pdftoppm`) are available, render sheets for visual review:
  - `soffice --headless --convert-to pdf --outdir $OUTDIR $INPUT_XLSX`
  - `pdftoppm -png $OUTDIR/$BASENAME.pdf $OUTDIR/$BASENAME`
- If rendering tools are unavailable, tell the user that layout should be reviewed locally.
- Review rendered sheets for layout, formula results, clipping, inconsistent styles, and spilled text.

## Dependencies (install if missing)
Prefer `uv` for dependency management.

Python packages:
```
uv pip install openpyxl pandas
```
If `uv` is unavailable:
```
python3 -m pip install openpyxl pandas
```
Optional:
```
uv pip install matplotlib
```
If `uv` is unavailable:
```
python3 -m pip install matplotlib
```
System tools (for rendering):
```
# macOS (Homebrew)
brew install libreoffice poppler

# Ubuntu/Debian
sudo apt-get install -y libreoffice poppler-utils
```

If installation is not possible in this environment, tell the user which dependency is missing and how to install it locally.

## Environment
No required environment variables.

## Examples
- Runnable examples (openpyxl): `references/examples/openpyxl/`

## Formula requirements
- Use formulas for derived values rather than hardcoding results.
- Do not use dynamic array functions like `FILTER`, `XLOOKUP`, `SORT`, or `SEQUENCE`.
- Keep formulas simple and legible; use helper cells for complex logic.
- Avoid volatile functions like `INDIRECT` and `OFFSET` unless required.
- Prefer cell references over magic numbers (for example, `=H6*(1+$B$3)` instead of `=H6*1.04`).
- Use absolute (`$B$4`) or relative (`B4`) references carefully so copied formulas behave correctly.
- If you need literal text that starts with `=`, prefix it with a single quote.
- Guard against `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, and `#NAME?` errors.
- Check for off-by-one mistakes, circular references, and incorrect ranges.

## Citation requirements
- Cite sources inside the spreadsheet using plain-text URLs.
- For financial models, cite model inputs in cell comments.
- For tabular data sourced externally, add a source column when each row represents a separate item.

## Formatting requirements (existing formatted spreadsheets)
- Render and inspect a provided spreadsheet before modifying it when possible.
- Preserve existing formatting and style exactly.
- Match styles for any newly filled cells that were previously blank.
- Never overwrite established formatting unless the user explicitly asks for a redesign.

## Formatting requirements (new or unstyled spreadsheets)
- Use appropriate number and date formats.
- Dates should render as dates, not plain numbers.
- Percentages should usually default to one decimal place unless the data calls for something else.
- Currencies should use the appropriate currency format.
- Headers should be visually distinct from raw inputs and derived cells.
- Use fill colors, borders, spacing, and merged cells sparingly and intentionally.
- Set row heights and column widths so content is readable without excessive whitespace.
- Do not apply borders around every filled cell.
- Group related calculations and make totals simple sums of the cells above them.
- Add whitespace to separate sections.
- Ensure text does not spill into adjacent cells.
- Avoid unsupported spreadsheet data-table features such as `=TABLE`.

## Color conventions (if no style guidance)
- Blue: user input
- Black: formulas and derived values
- Green: linked or imported values
- Gray: static constants
- Orange: review or caution
- Light red: error or flag
- Purple: control or logic
- Teal: visualization anchors and KPI highlights

## Finance-specific requirements
- Format zeros as `-`.
- Negative numbers should be red and in parentheses.
- Format multiples as `5.2x`.
- Always specify units in headers (for example, `Revenue ($mm)`).
- Cite sources for all raw inputs in cell comments.
- For new financial models with no user-specified style, use blue text for hardcoded inputs, black for formulas, green for internal workbook links, red for external links, and yellow fill for key assumptions that need attention.

## Investment banking layouts
If the spreadsheet is an IB-style model (LBO, DCF, 3-statement, valuation):
- Totals should sum the range directly above.
- Hide gridlines and use horizontal borders above totals across relevant columns.
- Section headers should be merged cells with dark fill and white text.
- Column labels for numeric data should be right-aligned; row labels should be left-aligned.
- Indent submetrics under their parent line items.

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, numbers

wb = Workbook()
ws = wb.active
ws.title = "Revenue Model"

# Headers
headers = ["Quarter", "Revenue ($mm)", "Costs ($mm)", "Margin (%)"]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal="center")

# Data rows
data = [
    ("Q1", 12.5, 8.0),
    ("Q2", 14.2, 8.5),
    ("Q3", 15.8, 9.1),
    ("Q4", 18.1, 9.8),
]
for row_idx, (quarter, revenue, costs) in enumerate(data, 2):
    ws.cell(row=row_idx, column=1, value=quarter)
    ws.cell(row=row_idx, column=2, value=revenue)
    ws.cell(row=row_idx, column=3, value=costs)
    # Margin formula: (Revenue - Costs) / Revenue
    ws.cell(row=row_idx, column=4).value = f"=(B{row_idx}-C{row_idx})/B{row_idx}"
    ws.cell(row=row_idx, column=4).number_format = "0.0%"

# Totals row
total_row = len(data) + 2
ws.cell(row=total_row, column=1, value="Total").font = Font(bold=True)
ws.cell(row=total_row, column=2).value = f"=SUM(B2:B{total_row - 1})"
ws.cell(row=total_row, column=3).value = f"=SUM(C2:C{total_row - 1})"

wb.save("output/spreadsheet/revenue_model.xlsx")
```
