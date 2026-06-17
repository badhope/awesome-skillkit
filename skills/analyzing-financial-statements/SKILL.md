---
name: analyzing-financial-statements
name_zh: 分析财务报表
description: 'This skill calculates key financial ratios and metrics from financial'
description_zh: 计算关键财务比率和指标，用于投资分析和公司评估。
category: finance
tags:
  - ai
  - api
  - evaluation
  - frontend
  - javascript
source: null
license: UNKNOWN
author: unknown
version: '0.1.0'
needs_review: false
slug: analyzing-financial-statements
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

Use this skill when you need guidance on analyzing financial statements.


# Inputs

User request or task description.

# Output

Generated content based on the user request.

# Prompt

Follow the guidelines in this skill when working on related tasks.

# Financial Ratio Calculator Skill

This skill provides comprehensive financial ratio analysis for evaluating company performance, profitability, liquidity, and valuation.

## Capabilities

Calculate and interpret:
- **Profitability Ratios**: ROE, ROA, Gross Margin, Operating Margin, Net Margin
- **Liquidity Ratios**: Current Ratio, Quick Ratio, Cash Ratio
- **Leverage Ratios**: Debt-to-Equity, Interest Coverage, Debt Service Coverage
- **Efficiency Ratios**: Asset Turnover, Inventory Turnover, Receivables Turnover
- **Valuation Ratios**: P/E, P/B, P/S, EV/EBITDA, PEG
- **Per-Share Metrics**: EPS, Book Value per Share, Dividend per Share

## How to Use

1. **Input Data**: Provide financial statement data (income statement, balance sheet, cash flow)
2. **Select Ratios**: Specify which ratios to calculate or use "all" for comprehensive analysis
3. **Interpretation**: The skill will calculate ratios and provide industry-standard interpretations

## Input Format

Financial data can be provided as:
- CSV with financial line items
- JSON with structured financial statements
- Text description of key financial figures
- Excel files with financial statements

## Output Format

Results include:
- Calculated ratios with values
- Industry benchmark comparisons (when available)
- Trend analysis (if multiple periods provided)
- Interpretation and insights
- Excel report with formatted results

## Example Usage

"Calculate key financial ratios for this company based on the attached financial statements"

"What's the P/E ratio if the stock price is $50 and annual earnings are $2.50 per share?"

"Analyze the liquidity position using the balance sheet data"

## Scripts

- `calculate_ratios.py`: Main calculation engine for all financial ratios
- `interpret_ratios.py`: Provides interpretation and benchmarking

## Best Practices

1. Always validate data completeness before calculations
2. Handle missing values appropriately (use industry averages or exclude)
3. Consider industry context when interpreting ratios
4. Include period comparisons for trend analysis
5. Flag unusual or concerning ratios

## Limitations

- Requires accurate financial data
- Industry benchmarks are general guidelines
- Some ratios may not apply to all industries
- Historical data doesn't guarantee future performance

# When NOT to use

Do not use this skill for tasks outside its scope.


# Example

See the skill content above for practical examples.


```python
# 使用 analyzing-financial-statements 技能
from skill_loader import load_skill

# 加载技能
skill = load_skill("analyzing-financial-statements")

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
