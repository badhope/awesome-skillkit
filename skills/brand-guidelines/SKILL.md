---
name: brand-guidelines
name_zh: brand-guidelines
description: 'Applies Anthropic''s official brand colors and typography to any sort of artifact that may benefit from having Anthropic''s look-and-feel. Use it when brand colors or style guidelines, visual formatt...'
description_zh: 'Applies Anthropic''s official brand colors and typography to any sort of artifact that may benefit from having Anthropic''s look-and-feel. Use it when brand colors or style guidelines, visual formatt...'
category: documentation
tags:
  - ai
  - api
  - frontend
  - llm
  - python
source: null
license: Complete terms in LICENSE.txt
needs_review: false
slug: brand-guidelines
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
---
# When to use

Use this skill when you need guidance on brand-guidelines.

# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Anthropic Brand Styling

## Overview

To access Anthropic's official brand identity and style resources, use this skill.

**Keywords**: branding, corporate identity, visual identity, post-processing, styling, brand colors, typography, Anthropic brand, visual formatting, visual design

## Brand Guidelines

### Colors

**Main Colors:**

- Dark: `#141413` - Primary text and dark backgrounds
- Light: `#faf9f5` - Light backgrounds and text on dark
- Mid Gray: `#b0aea5` - Secondary elements
- Light Gray: `#e8e6dc` - Subtle backgrounds

**Accent Colors:**

- Orange: `#d97757` - Primary accent
- Blue: `#6a9bcc` - Secondary accent
- Green: `#788c5d` - Tertiary accent

### Typography

- **Headings**: Poppins (with Arial fallback)
- **Body Text**: Lora (with Georgia fallback)
- **Note**: Fonts should be pre-installed in your environment for best results

## Features

### Smart Font Application

- Applies Poppins font to headings (24pt and larger)
- Applies Lora font to body text
- Automatically falls back to Arial/Georgia if custom fonts unavailable
- Preserves readability across all systems

### Text Styling

- Headings (24pt+): Poppins font
- Body text: Lora font
- Smart color selection based on background
- Preserves text hierarchy and formatting

### Shape and Accent Colors

- Non-text shapes use accent colors
- Cycles through orange, blue, and green accents
- Maintains visual interest while staying on-brand

## Technical Details

### Font Management

- Uses system-installed Poppins and Lora fonts when available
- Provides automatic fallback to Arial (headings) and Georgia (body)
- No font installation required - works with existing system fonts
- For best results, pre-install Poppins and Lora fonts in your environment

### Color Application

- Uses RGB color values for precise brand matching
- Applied via python-pptx's RGBColor class
- Maintains color fidelity across different systems

# When NOT to use

Do not use this skill for tasks outside its scope.

# Example

See the skill content above for practical examples.


# Example

```python
# Use the brand-guidelines skill
from skill_loader import load_skill

skill = load_skill("brand-guidelines")
result = skill.execute(params={"key": "value"})
print(result)
```

