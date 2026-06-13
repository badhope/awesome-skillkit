---
name: applying-brand-guidelines
name_zh: 应用品牌指南
description: This skill applies consistent corporate branding and styling to all
  generated
description_zh: 确保内容符合品牌指南，包括视觉、语调和消息传递。
category: dev-tools
tags:
  - ai
  - cli
  - documentation
  - frontend
  - llm
source:
license: UNKNOWN
author: unknown
version: 0.1.0
needs_review: false
slug: applying-brand-guidelines
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
---
# When to use

Use this skill when you need guidance on applying brand guidelines.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Corporate Brand Guidelines Skill

This skill ensures all generated documents adhere to corporate brand standards for consistent, professional communication.

## Brand Identity

### Company: Acme Corporation
**Tagline**: "Innovation Through Excellence"
**Industry**: Technology Solutions

## Visual Standards

### Color Palette

**Primary Colors**:
- **Acme Blue**: #0066CC (RGB: 0, 102, 204) - Headers, primary buttons
- **Acme Navy**: #003366 (RGB: 0, 51, 102) - Text, accents
- **White**: #FFFFFF - Backgrounds, reverse text

**Secondary Colors**:
- **Success Green**: #28A745 (RGB: 40, 167, 69) - Positive metrics
- **Warning Amber**: #FFC107 (RGB: 255, 193, 7) - Cautions
- **Error Red**: #DC3545 (RGB: 220, 53, 69) - Negative values
- **Neutral Gray**: #6C757D (RGB: 108, 117, 125) - Secondary text

### Typography

**Primary Font Family**: Segoe UI, system-ui, -apple-system, sans-serif

**Font Hierarchy**:
- **H1**: 32pt, Bold, Acme Blue
- **H2**: 24pt, Semibold, Acme Navy
- **H3**: 18pt, Semibold, Acme Navy
- **Body**: 11pt, Regular, Acme Navy
- **Caption**: 9pt, Regular, Neutral Gray

### Logo Usage

- Position: Top-left corner on first page/slide
- Size: 120px width (maintain aspect ratio)
- Clear space: Minimum 20px padding on all sides
- Never distort, rotate, or apply effects

## Document Standards

### PowerPoint Presentations

**Slide Templates**:
1. **Title Slide**: Company logo, presentation title, date, presenter
2. **Section Divider**: Section title with blue background
3. **Content Slide**: Title bar with blue background, white content area
4. **Data Slide**: For charts/graphs, maintain color palette

**Layout Rules**:
- Margins: 0.5 inches all sides
- Title position: Top 15% of slide
- Bullet indentation: 0.25 inches per level
- Maximum 6 bullet points per slide
- Charts use brand colors exclusively

### Excel Spreadsheets

**Formatting Standards**:
- **Headers**: Row 1, Bold, White text on Acme Blue background
- **Subheaders**: Bold, Acme Navy text
- **Data cells**: Regular, Acme Navy text
- **Borders**: Thin, Neutral Gray
- **Alternating rows**: Light gray (#F8F9FA) for readability

**Chart Defaults**:
- Primary series: Acme Blue
- Secondary series: Success Green
- Gridlines: Neutral Gray, 0.5pt
- No 3D effects or gradients

### PDF Documents

**Page Layout**:
- **Header**: Company logo left, document title center, page number right
- **Footer**: Copyright notice left, date center, classification right
- **Margins**: 1 inch all sides
- **Line spacing**: 1.15
- **Paragraph spacing**: 12pt after

**Section Formatting**:
- Main headings: Acme Blue, 16pt, bold
- Subheadings: Acme Navy, 14pt, semibold
- Body text: Acme Navy, 11pt, regular

## Content Guidelines

### Tone of Voice

- **Professional**: Formal but approachable
- **Clear**: Avoid jargon, use simple language
- **Active**: Use active voice, action-oriented
- **Positive**: Focus on solutions and benefits

### Standard Phrases

**Opening Statements**:
- "At Acme Corporation, we..."
- "Our commitment to innovation..."
- "Delivering excellence through..."

**Closing Statements**:
- "Thank you for your continued partnership."
- "We look forward to serving your needs."
- "Together, we achieve excellence."

### Data Presentation

**Numbers**:
- Use comma separators for thousands
- Currency: $X,XXX.XX format
- Percentages: XX.X% (one decimal)
- Dates: Month DD, YYYY

**Tables**:
- Headers in brand blue
- Alternating row colors
- Right-align numbers
- Left-align text

## Quality Standards

### Before Finalizing

Always ensure:
1. Logo is properly placed and sized
2. All colors match brand palette exactly
3. Fonts are consistent throughout
4. No typos or grammatical errors
5. Data is accurately presented
6. Professional tone maintained

### Prohibited Elements

Never use:
- Clip art or stock photos without approval
- Comic Sans, Papyrus, or decorative fonts
- Rainbow colors or gradients
- Animations or transitions (unless specified)
- Competitor branding or references

## Application Instructions

When creating any document:
1. Start with brand colors and fonts
2. Apply appropriate template structure
3. Include logo on first page/slide
4. Use consistent formatting throughout
5. Review against brand standards
6. Ensure professional appearance

## Scripts

- `apply_brand.py`: Automatically applies brand formatting to documents
- `validate_brand.py`: Checks documents for brand compliance

## Notes

- These guidelines apply to all external communications
- Internal documents may use simplified formatting
- Special projects may have exceptions (request approval)
- Brand guidelines updated quarterly - check for latest version

# When NOT to use

Do not use this skill for tasks outside its scope.


# Example

See the skill content above for practical examples.


```python
# 使用 applying-brand-guidelines 技能
from skill_loader import load_skill

# 加载技能
skill = load_skill("applying-brand-guidelines")

# 执行技能
result = skill.execute(
    params={"key": "value"},
    options={"verbose": True}
)

# 处理结果
if result.success:
    print(f"Success: {result.output}")
else:
    print(f"Error: {result.error}")
```
