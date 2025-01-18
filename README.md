# Streamlit Dashboard for NPS Analysis

This project provides a **Streamlit dashboard** for analyzing Net Promoter Score (NPS) data, focusing on customer feedback and reasons related to various insurance processes. The dashboard is designed to handle **Jalali and Gregorian dates**, visualize data effectively, and support business insights generation.

---

## Features

- **Jalali-Gregorian Date Conversion**: Enables seamless filtering and manipulation of dates.
- **Dynamic Data Analysis**:
  - Generates pivot tables for NPS data based on insurance type.
  - Supports `thirdparty` and `carbody` insurance types.
- **Visualization Tools**:
  - Heatmaps for analyzing NPS scores against customer feedback reasons.
  - Group-level and overall NPS score visualizations.
- **Interactive User Input**:
  - Select NPS groups (`Promoter`, `Detractor`, `All`) or reason groups for customized analysis.

---

## Requirements

The project uses the following libraries:

- `streamlit`
- `numpy`
- `pandas`
- `jdatetime`
- `matplotlib`
- `seaborn`
- `arabic_reshaper`
- `bidi.algorithm`

Install the dependencies using:

```bash
pip install -r requirements.txt
