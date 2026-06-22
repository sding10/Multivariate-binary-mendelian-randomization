import pandas as pd
from pathlib import Path

# ============================================================
# MASTER SCRIPT:
# Create one consolidated supplementary workbook with 18 sheets
#
# Output sheet order:
#   ST1  - ST6   : Bias tables
#   ST7  - ST12  : Coverage, type I error, and power tables
#   ST13 - ST18  : First-stage F-statistic tables
# ============================================================


# ============================================================
# 1. Input and output paths
# ============================================================

base_dir = Path(
    r"C:\Users\sande\Desktop\Academics\RESEARCH\Dr Tiwari\Mendelian randomization project\Research paper 2\8000 simulation results-selected"
)

bias_file_path = base_dir / "Supplementary_Table1_b01.xlsx"
coverage_file_path = base_dir / "Supplementary_Table2_b01.xlsx"
f_file_path = base_dir / "Supplementary_Table3_FirstStage_F_b1_0_1.xlsx"

output_dir = (base_dir / ".." / "Resubmission").resolve()
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "Supplementary Tables.xlsx"


# ============================================================
# 2. Global user settings
# ============================================================

confounding_values = [0.5, 1.0, 1.5]

methods_order = ["2SPS", "2SRI", "GMM", "IV-MVB"]

# Scenario A/B settings: compare across IV strengths at fixed N = 1000
sample_size_value_AB = 1000

scenario_A = "Scenario A"
scenario_B = "Scenario B"
b1_A = 0
b1_B = 1

iv_order = [
    "Very Weak IVs",
    "Weak IVs",
    "Moderate IVs",
    "Strong IVs",
    "Very Strong IVs"
]

# Scenario C/D settings: compare across sample sizes under weak IVs
scenario_C = "Scenario C"
scenario_D = "Scenario D"
b1_C = 0
b1_D = 1

weak_iv_label = "Weak IVs"

sample_size_order_CD = [500, 1500, 2500, 5000, 7500, 10000]

# Metric columns
bias_col = "Bias, median (Q1, Q3)"
coverage_col = "Coverage"
type1_col_candidates = ["Type I error", "Type 1 error"]
power_col = "Power"

f_value_cols = ["McFadden F", "Cox-Snell F", "Nagelkerke F"]


# ============================================================
# 3. General helper functions
# ============================================================

def clean_excel_sheet_name(name):
    """Ensures sheet names are valid for Excel."""
    invalid_chars = ["[", "]", ":", "*", "?", "/", "\\"]
    for ch in invalid_chars:
        name = name.replace(ch, "_")
    return name[:31]


def format_cell_value(value):
    """Return blank string for missing values; otherwise return the value."""
    if pd.isna(value):
        return ""
    return value


def standardize_common_columns(df):
    """Standardizes common simulation-design columns."""
    df.columns = df.columns.str.strip()

    if "Scenario" in df.columns:
        df["Scenario"] = df["Scenario"].astype(str).str.strip()

    if "IV strength" in df.columns:
        df["IV strength"] = df["IV strength"].astype(str).str.strip()

    if "Method" in df.columns:
        df["Method"] = df["Method"].astype(str).str.strip()

    for col in ["b1", "Sample size", "c_x", "c_y", "Converged"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Keep the same logic as the original scripts:
    # if c_y exists, retain only rows where c_x = c_y.
    if "c_y" in df.columns and "c_x" in df.columns:
        df = df[df["c_x"] == df["c_y"]].copy()

    return df


def validate_columns(df, required_cols, file_label):
    """Raises a clear error if required columns are missing."""
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"{file_label} is missing the following required columns: {missing_cols}"
        )


# ============================================================
# 4. Read and clean input data
# ============================================================

# ----------------------------
# Bias data
# ----------------------------
bias_df = pd.read_excel(bias_file_path, sheet_name="Sheet1")
bias_df = standardize_common_columns(bias_df)

required_bias_cols = [
    "Scenario", "IV strength", "Method", "b1", "Sample size",
    "c_x", "Converged", bias_col
]
validate_columns(bias_df, required_bias_cols, "Bias input file")

bias_df["Converged"] = pd.to_numeric(bias_df["Converged"], errors="coerce")


# ----------------------------
# Coverage / type I error / power data
# ----------------------------
coverage_df = pd.read_excel(coverage_file_path, sheet_name="Sheet1")
coverage_df = standardize_common_columns(coverage_df)

type1_col = None
for candidate in type1_col_candidates:
    if candidate in coverage_df.columns:
        type1_col = candidate
        break

if type1_col is None:
    raise ValueError(
        f"Coverage input file does not contain a Type I error column. "
        f"Tried: {type1_col_candidates}"
    )

required_coverage_cols = [
    "Scenario", "IV strength", "Method", "b1", "Sample size",
    "c_x", coverage_col, type1_col, power_col
]
validate_columns(coverage_df, required_coverage_cols, "Coverage input file")

coverage_df[coverage_col] = pd.to_numeric(coverage_df[coverage_col], errors="coerce")
coverage_df[type1_col] = pd.to_numeric(coverage_df[type1_col], errors="coerce")
coverage_df[power_col] = pd.to_numeric(coverage_df[power_col], errors="coerce")


# ----------------------------
# First-stage F data
# ----------------------------
f_df = pd.read_excel(f_file_path, sheet_name="Sheet1")
f_df = standardize_common_columns(f_df)

required_f_cols = [
    "Scenario", "b1", "Sample size", "IV strength", "c_x",
    "McFadden F", "Cox-Snell F", "Nagelkerke F"
]
validate_columns(f_df, required_f_cols, "First-stage F input file")


# ============================================================
# 5. Bias table builders
# ============================================================

def get_bias_ab_value(data, scenario, b1_value, c_value, iv_strength, method):
    """Extracts Num Converged and Bias for one A/B design setting."""
    temp = data[
        (data["Scenario"] == scenario) &
        (data["b1"] == b1_value) &
        (data["Sample size"] == sample_size_value_AB) &
        (data["c_x"] == c_value) &
        (data["IV strength"] == iv_strength) &
        (data["Method"] == method)
    ].copy()

    if temp.empty:
        return "", ""

    temp = temp.sort_values(
        ["Scenario", "b1", "Sample size", "c_x", "IV strength", "Method"]
    )

    converged = format_cell_value(temp["Converged"].iloc[0])
    bias = format_cell_value(temp[bias_col].iloc[0])

    if converged != "":
        converged = int(converged)

    return converged, bias


def get_bias_cd_value(data, scenario, b1_value, c_value, sample_size, method):
    """Extracts Num Converged and Bias for one C/D design setting."""
    temp = data[
        (data["Scenario"] == scenario) &
        (data["b1"] == b1_value) &
        (data["Sample size"] == sample_size) &
        (data["c_x"] == c_value) &
        (data["IV strength"] == weak_iv_label) &
        (data["Method"] == method)
    ].copy()

    if temp.empty:
        return "", ""

    temp = temp.sort_values(
        ["Scenario", "b1", "Sample size", "c_x", "IV strength", "Method"]
    )

    converged = format_cell_value(temp["Converged"].iloc[0])
    bias = format_cell_value(temp[bias_col].iloc[0])

    if converged != "":
        converged = int(converged)

    return converged, bias


def build_bias_ab_table(data, c_value):
    """Builds Scenario A/B bias table for one confounding strength."""
    rows = []

    for iv_strength in iv_order:
        for method in methods_order:
            conv_A, bias_A = get_bias_ab_value(
                data, scenario_A, b1_A, c_value, iv_strength, method
            )
            conv_B, bias_B = get_bias_ab_value(
                data, scenario_B, b1_B, c_value, iv_strength, method
            )

            rows.append({
                "Group": iv_strength,
                "MR Method": method,
                "Scenario A Num Converged": conv_A,
                "Scenario A Median (Q1, Q3) Bias": bias_A,
                "Scenario B Num Converged": conv_B,
                "Scenario B Median (Q1, Q3) Bias": bias_B
            })

    return pd.DataFrame(rows)


def build_bias_cd_table(data, c_value):
    """Builds Scenario C/D bias table for one confounding strength."""
    rows = []

    for sample_size in sample_size_order_CD:
        for method in methods_order:
            conv_C, bias_C = get_bias_cd_value(
                data, scenario_C, b1_C, c_value, sample_size, method
            )
            conv_D, bias_D = get_bias_cd_value(
                data, scenario_D, b1_D, c_value, sample_size, method
            )

            rows.append({
                "Group": sample_size,
                "MR Method": method,
                "Scenario C Num Converged": conv_C,
                "Scenario C Median (Q1, Q3) Bias": bias_C,
                "Scenario D Num Converged": conv_D,
                "Scenario D Median (Q1, Q3) Bias": bias_D
            })

    return pd.DataFrame(rows)


# ============================================================
# 6. Coverage/type I error/power table builders
# ============================================================

def get_coverage_ab_value(data, scenario, b1_value, c_value, iv_strength, method, second_metric_col):
    """Extracts Coverage and second metric for one A/B design setting."""
    temp = data[
        (data["Scenario"] == scenario) &
        (data["b1"] == b1_value) &
        (data["Sample size"] == sample_size_value_AB) &
        (data["c_x"] == c_value) &
        (data["IV strength"] == iv_strength) &
        (data["Method"] == method)
    ].copy()

    if temp.empty:
        return "", ""

    temp = temp.sort_values(
        ["Scenario", "b1", "Sample size", "c_x", "IV strength", "Method"]
    )

    coverage = format_cell_value(temp[coverage_col].iloc[0])
    second_metric = format_cell_value(temp[second_metric_col].iloc[0])

    return coverage, second_metric


def get_coverage_cd_value(data, scenario, b1_value, c_value, sample_size, method, second_metric_col):
    """Extracts Coverage and second metric for one C/D design setting."""
    temp = data[
        (data["Scenario"] == scenario) &
        (data["b1"] == b1_value) &
        (data["Sample size"] == sample_size) &
        (data["c_x"] == c_value) &
        (data["IV strength"] == weak_iv_label) &
        (data["Method"] == method)
    ].copy()

    if temp.empty:
        return "", ""

    temp = temp.sort_values(
        ["Scenario", "b1", "Sample size", "c_x", "IV strength", "Method"]
    )

    coverage = format_cell_value(temp[coverage_col].iloc[0])
    second_metric = format_cell_value(temp[second_metric_col].iloc[0])

    return coverage, second_metric


def build_coverage_ab_table(data, c_value):
    """
    Builds Scenario A/B table.
    Scenario A: Coverage + Type I error.
    Scenario B: Coverage + Power.
    """
    rows = []

    for iv_strength in iv_order:
        for method in methods_order:
            cov_A, type1_A = get_coverage_ab_value(
                data, scenario_A, b1_A, c_value, iv_strength, method, type1_col
            )
            cov_B, power_B = get_coverage_ab_value(
                data, scenario_B, b1_B, c_value, iv_strength, method, power_col
            )

            rows.append({
                "Group": iv_strength,
                "MR Method": method,
                "Scenario A Coverage": cov_A,
                "Scenario A Type I error": type1_A,
                "Scenario B Coverage": cov_B,
                "Scenario B Power": power_B
            })

    return pd.DataFrame(rows)


def build_coverage_cd_table(data, c_value):
    """
    Builds Scenario C/D table.
    Scenario C: Coverage + Type I error.
    Scenario D: Coverage + Power.
    """
    rows = []

    for sample_size in sample_size_order_CD:
        for method in methods_order:
            cov_C, type1_C = get_coverage_cd_value(
                data, scenario_C, b1_C, c_value, sample_size, method, type1_col
            )
            cov_D, power_D = get_coverage_cd_value(
                data, scenario_D, b1_D, c_value, sample_size, method, power_col
            )

            rows.append({
                "Group": sample_size,
                "MR Method": method,
                "Scenario C Coverage": cov_C,
                "Scenario C Type I error": type1_C,
                "Scenario D Coverage": cov_D,
                "Scenario D Power": power_D
            })

    return pd.DataFrame(rows)


# ============================================================
# 7. First-stage F table builders
# ============================================================

def get_f_values(data, scenario, b1_value, c_value, sample_size, iv_strength):
    """
    Extracts the three first-stage F summaries for one design setting.
    These summaries do not vary by MR method.
    """
    temp = data[
        (data["Scenario"] == scenario) &
        (data["b1"] == b1_value) &
        (data["Sample size"] == sample_size) &
        (data["c_x"] == c_value) &
        (data["IV strength"] == iv_strength)
    ].copy()

    if temp.empty:
        return {col: "" for col in f_value_cols}

    temp = temp.sort_values(
        ["Scenario", "b1", "Sample size", "c_x", "IV strength"]
    )

    return {col: format_cell_value(temp[col].iloc[0]) for col in f_value_cols}


def build_f_ab_table(f_data, c_value):
    """
    Builds Scenario A/B first-stage F table for one confounding strength.

    F-statistic summaries are first-stage design-level quantities.
    They do not vary by MR estimation method, so MR Method and Num Converged
    are intentionally not included in ST13-ST15.
    """
    rows = []

    for iv_strength in iv_order:
        f_A = get_f_values(
            f_data,
            scenario_A,
            b1_A,
            c_value,
            sample_size_value_AB,
            iv_strength
        )

        f_B = get_f_values(
            f_data,
            scenario_B,
            b1_B,
            c_value,
            sample_size_value_AB,
            iv_strength
        )

        rows.append({
            "Group": iv_strength,
            "Scenario A McFadden F": f_A["McFadden F"],
            "Scenario A Cox-Snell F": f_A["Cox-Snell F"],
            "Scenario A Nagelkerke F": f_A["Nagelkerke F"],
            "Scenario B McFadden F": f_B["McFadden F"],
            "Scenario B Cox-Snell F": f_B["Cox-Snell F"],
            "Scenario B Nagelkerke F": f_B["Nagelkerke F"]
        })

    return pd.DataFrame(rows)


def build_f_cd_table(f_data, c_value):
    """
    Builds Scenario C/D first-stage F table for one confounding strength.

    F-statistic summaries are first-stage design-level quantities.
    They do not vary by MR estimation method, so MR Method and Num Converged
    are intentionally not included in ST16-ST18.
    """
    rows = []

    for sample_size in sample_size_order_CD:
        f_C = get_f_values(
            f_data,
            scenario_C,
            b1_C,
            c_value,
            sample_size,
            weak_iv_label
        )

        f_D = get_f_values(
            f_data,
            scenario_D,
            b1_D,
            c_value,
            sample_size,
            weak_iv_label
        )

        rows.append({
            "Group": sample_size,
            "Scenario C McFadden F": f_C["McFadden F"],
            "Scenario C Cox-Snell F": f_C["Cox-Snell F"],
            "Scenario C Nagelkerke F": f_C["Nagelkerke F"],
            "Scenario D McFadden F": f_D["McFadden F"],
            "Scenario D Cox-Snell F": f_D["Cox-Snell F"],
            "Scenario D Nagelkerke F": f_D["Nagelkerke F"]
        })

    return pd.DataFrame(rows)


# ============================================================
# 8. Excel formatting
# ============================================================

def make_formats(workbook):
    """Creates all Excel formats used in the workbook."""
    return {
        "title": workbook.add_format({
            "bold": True,
            "font_size": 13,
            "align": "center",
            "valign": "vcenter",
            "bg_color": "#D9EAF7",
            "border": 1
        }),
        "top_header": workbook.add_format({
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "bg_color": "#4A6984",
            "font_color": "white",
            "border": 1,
            "text_wrap": True
        }),
        "sub_header": workbook.add_format({
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "bg_color": "#D9EAF7",
            "border": 1,
            "text_wrap": True
        }),
        "group": workbook.add_format({
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "bg_color": "#F2F2F2",
            "text_wrap": True
        }),
        "method": workbook.add_format({
            "align": "center",
            "valign": "vcenter",
            "border": 1
        }),
        "int": workbook.add_format({
            "num_format": "0",
            "align": "center",
            "valign": "vcenter",
            "border": 1
        }),
        "bias": workbook.add_format({
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "text_wrap": False
        }),
        "metric": workbook.add_format({
            "num_format": "0.000",
            "align": "center",
            "valign": "vcenter",
            "border": 1
        }),
        "f_value": workbook.add_format({
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "text_wrap": False
        }),
        "missing": workbook.add_format({
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "bg_color": "#F4CCCC",
            "font_color": "#990000"
        }),
        "note": workbook.add_format({
            "italic": True,
            "font_size": 9,
            "align": "left",
            "valign": "top",
            "text_wrap": True
        })
    }


def write_integer_or_missing(worksheet, row, col, value, formats):
    """Writes an integer value or a Missing flag."""
    if value == "" or pd.isna(value):
        worksheet.write(row, col, "Missing", formats["missing"])
    else:
        worksheet.write_number(row, col, int(value), formats["int"])


def write_text_or_missing(worksheet, row, col, value, value_format, formats):
    """Writes text-like value or a Missing flag."""
    if value == "" or pd.isna(value):
        worksheet.write(row, col, "Missing", formats["missing"])
    else:
        worksheet.write(row, col, value, value_format)


def write_metric_or_missing(worksheet, row, col, value, formats):
    """Writes numeric metric value or a Missing flag."""
    if value == "" or pd.isna(value):
        worksheet.write(row, col, "Missing", formats["missing"])
    else:
        worksheet.write_number(row, col, float(value), formats["metric"])


# ============================================================
# 9. Sheet writers
# ============================================================

def write_bias_sheet(
    workbook,
    sheet_name,
    table,
    title_text,
    group_header,
    scenario_left,
    scenario_right,
    note_text,
    group_values,
    formats,
    group_col_width
):
    """Writes one formatted bias sheet."""
    worksheet = workbook.add_worksheet(clean_excel_sheet_name(sheet_name))

    worksheet.merge_range("A1:F1", title_text, formats["title"])

    worksheet.merge_range("A2:A3", group_header, formats["top_header"])
    worksheet.merge_range("B2:B3", "MR Method", formats["top_header"])
    worksheet.merge_range("C2:D2", scenario_left, formats["top_header"])
    worksheet.merge_range("E2:F2", scenario_right, formats["top_header"])

    worksheet.write("C3", "Num Converged", formats["sub_header"])
    worksheet.write("D3", "Median (Q1, Q3) Bias", formats["sub_header"])
    worksheet.write("E3", "Num Converged", formats["sub_header"])
    worksheet.write("F3", "Median (Q1, Q3) Bias", formats["sub_header"])

    start_row = 3
    current_row = start_row

    for group_value in group_values:
        block = table[table["Group"] == group_value].copy()

        worksheet.merge_range(
            current_row, 0,
            current_row + len(methods_order) - 1, 0,
            group_value,
            formats["group"]
        )

        for i, method in enumerate(methods_order):
            excel_row = current_row + i
            row_data = block[block["MR Method"] == method].iloc[0]

            worksheet.write(excel_row, 1, row_data["MR Method"], formats["method"])

            write_integer_or_missing(
                worksheet, excel_row, 2,
                row_data[f"{scenario_left} Num Converged"],
                formats
            )
            write_text_or_missing(
                worksheet, excel_row, 3,
                row_data[f"{scenario_left} Median (Q1, Q3) Bias"],
                formats["bias"],
                formats
            )
            write_integer_or_missing(
                worksheet, excel_row, 4,
                row_data[f"{scenario_right} Num Converged"],
                formats
            )
            write_text_or_missing(
                worksheet, excel_row, 5,
                row_data[f"{scenario_right} Median (Q1, Q3) Bias"],
                formats["bias"],
                formats
            )

        current_row += len(methods_order)

    note_row = current_row + 2
    worksheet.merge_range(note_row, 0, note_row + 1, 5, note_text, formats["note"])

    worksheet.set_column("A:A", group_col_width)
    worksheet.set_column("B:B", 12)
    worksheet.set_column("C:C", 16)
    worksheet.set_column("D:D", 24)
    worksheet.set_column("E:E", 16)
    worksheet.set_column("F:F", 24)

    worksheet.set_row(0, 26)
    worksheet.set_row(1, 28)
    worksheet.set_row(2, 34)

    for r in range(start_row, current_row):
        worksheet.set_row(r, 22)

    worksheet.freeze_panes(3, 0)
    worksheet.set_landscape()
    worksheet.fit_to_pages(1, 1)
    worksheet.set_margins(left=0.3, right=0.3, top=0.5, bottom=0.5)


def write_coverage_sheet(
    workbook,
    sheet_name,
    table,
    title_text,
    group_header,
    scenario_left,
    scenario_right,
    note_text,
    group_values,
    formats,
    group_col_width
):
    """Writes one formatted coverage/type I error/power sheet."""
    worksheet = workbook.add_worksheet(clean_excel_sheet_name(sheet_name))

    worksheet.merge_range("A1:F1", title_text, formats["title"])

    worksheet.merge_range("A2:A3", group_header, formats["top_header"])
    worksheet.merge_range("B2:B3", "MR Method", formats["top_header"])
    worksheet.merge_range("C2:D2", scenario_left, formats["top_header"])
    worksheet.merge_range("E2:F2", scenario_right, formats["top_header"])

    worksheet.write("C3", "Coverage", formats["sub_header"])
    worksheet.write("D3", "Type I error", formats["sub_header"])
    worksheet.write("E3", "Coverage", formats["sub_header"])
    worksheet.write("F3", "Power", formats["sub_header"])

    start_row = 3
    current_row = start_row

    for group_value in group_values:
        block = table[table["Group"] == group_value].copy()

        worksheet.merge_range(
            current_row, 0,
            current_row + len(methods_order) - 1, 0,
            group_value,
            formats["group"]
        )

        for i, method in enumerate(methods_order):
            excel_row = current_row + i
            row_data = block[block["MR Method"] == method].iloc[0]

            worksheet.write(excel_row, 1, row_data["MR Method"], formats["method"])

            write_metric_or_missing(
                worksheet, excel_row, 2,
                row_data[f"{scenario_left} Coverage"],
                formats
            )
            write_metric_or_missing(
                worksheet, excel_row, 3,
                row_data[f"{scenario_left} Type I error"],
                formats
            )
            write_metric_or_missing(
                worksheet, excel_row, 4,
                row_data[f"{scenario_right} Coverage"],
                formats
            )
            write_metric_or_missing(
                worksheet, excel_row, 5,
                row_data[f"{scenario_right} Power"],
                formats
            )

        current_row += len(methods_order)

    note_row = current_row + 2
    worksheet.merge_range(note_row, 0, note_row + 1, 5, note_text, formats["note"])

    worksheet.set_column("A:A", group_col_width)
    worksheet.set_column("B:B", 12)
    worksheet.set_column("C:F", 16)

    worksheet.set_row(0, 26)
    worksheet.set_row(1, 28)
    worksheet.set_row(2, 34)

    for r in range(start_row, current_row):
        worksheet.set_row(r, 22)

    worksheet.freeze_panes(3, 0)
    worksheet.set_landscape()
    worksheet.fit_to_pages(1, 1)
    worksheet.set_margins(left=0.3, right=0.3, top=0.5, bottom=0.5)


def write_f_sheet(
    workbook,
    sheet_name,
    table,
    title_text,
    group_header,
    scenario_left,
    scenario_right,
    note_text,
    group_values,
    formats,
    group_col_width
):
    """
    Writes one formatted first-stage F-statistic sheet.

    Header design is retained in the same style as ST1-ST12:
      - merged title row
      - dark scenario-level headers
      - light subheaders
      - grouped first column
      - bottom note row

    MR Method and Num Converged are intentionally omitted because
    first-stage F-statistic summaries do not vary by MR method.
    """
    worksheet = workbook.add_worksheet(clean_excel_sheet_name(sheet_name))

    worksheet.merge_range("A1:G1", title_text, formats["title"])

    worksheet.merge_range("A2:A3", group_header, formats["top_header"])
    worksheet.merge_range("B2:D2", scenario_left, formats["top_header"])
    worksheet.merge_range("E2:G2", scenario_right, formats["top_header"])

    worksheet.write("B3", "McFadden F", formats["sub_header"])
    worksheet.write("C3", "Cox-Snell F", formats["sub_header"])
    worksheet.write("D3", "Nagelkerke F", formats["sub_header"])

    worksheet.write("E3", "McFadden F", formats["sub_header"])
    worksheet.write("F3", "Cox-Snell F", formats["sub_header"])
    worksheet.write("G3", "Nagelkerke F", formats["sub_header"])

    start_row = 3
    current_row = start_row

    for group_value in group_values:
        block = table[table["Group"] == group_value].copy()

        if block.empty:
            worksheet.write(current_row, 0, group_value, formats["group"])
            for col in range(1, 7):
                worksheet.write(current_row, col, "Missing", formats["missing"])
            current_row += 1
            continue

        row_data = block.iloc[0]

        worksheet.write(current_row, 0, group_value, formats["group"])

        write_text_or_missing(
            worksheet, current_row, 1,
            row_data[f"{scenario_left} McFadden F"],
            formats["f_value"], formats
        )
        write_text_or_missing(
            worksheet, current_row, 2,
            row_data[f"{scenario_left} Cox-Snell F"],
            formats["f_value"], formats
        )
        write_text_or_missing(
            worksheet, current_row, 3,
            row_data[f"{scenario_left} Nagelkerke F"],
            formats["f_value"], formats
        )

        write_text_or_missing(
            worksheet, current_row, 4,
            row_data[f"{scenario_right} McFadden F"],
            formats["f_value"], formats
        )
        write_text_or_missing(
            worksheet, current_row, 5,
            row_data[f"{scenario_right} Cox-Snell F"],
            formats["f_value"], formats
        )
        write_text_or_missing(
            worksheet, current_row, 6,
            row_data[f"{scenario_right} Nagelkerke F"],
            formats["f_value"], formats
        )

        current_row += 1

    note_row = current_row + 2
    worksheet.merge_range(note_row, 0, note_row + 1, 6, note_text, formats["note"])

    worksheet.set_column("A:A", group_col_width)
    worksheet.set_column("B:G", 22)

    worksheet.set_row(0, 26)
    worksheet.set_row(1, 28)
    worksheet.set_row(2, 34)

    for r in range(start_row, current_row):
        worksheet.set_row(r, 22)

    worksheet.freeze_panes(3, 0)
    worksheet.set_landscape()
    worksheet.fit_to_pages(1, 1)
    worksheet.set_margins(left=0.3, right=0.3, top=0.5, bottom=0.5)


# ============================================================
# 10. Create the consolidated workbook
# ============================================================

with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    workbook = writer.book
    formats = make_formats(workbook)

    st_number = 1

    # --------------------------------------------------------
    # ST1-ST3: Bias, Scenarios A/B
    # --------------------------------------------------------
    for c_value in confounding_values:
        table = build_bias_ab_table(bias_df, c_value)

        write_bias_sheet(
            workbook=workbook,
            sheet_name=f"ST{st_number}",
            table=table,
            title_text=(
                f"Supplementary Table {st_number}: Bias comparison for "
                f"Scenarios A and B (c_x = c_y = {c_value})"
            ),
            group_header="Instrument Strength",
            scenario_left="Scenario A",
            scenario_right="Scenario B",
            note_text=(
                "Note. Scenario A corresponds to beta_1 = 0, and Scenario B corresponds "
                "to beta_1 = 1. Both scenarios use sample size N = 1000. Bias is reported "
                "as median (Q1, Q3). Tables are stratified by confounding strength c_x = c_y."
            ),
            group_values=iv_order,
            formats=formats,
            group_col_width=22
        )

        st_number += 1

    # --------------------------------------------------------
    # ST4-ST6: Bias, Scenarios C/D
    # --------------------------------------------------------
    for c_value in confounding_values:
        table = build_bias_cd_table(bias_df, c_value)

        write_bias_sheet(
            workbook=workbook,
            sheet_name=f"ST{st_number}",
            table=table,
            title_text=(
                f"Supplementary Table {st_number}: Bias comparison for "
                f"Scenarios C and D (c_x = c_y = {c_value})"
            ),
            group_header="Sample Size",
            scenario_left="Scenario C",
            scenario_right="Scenario D",
            note_text=(
                "Note. Scenario C corresponds to beta_1 = 0, and Scenario D corresponds "
                "to beta_1 = 1. Both scenarios use weak IVs and vary the sample size. Bias "
                "is reported as median (Q1, Q3). Tables are stratified by confounding "
                "strength c_x = c_y."
            ),
            group_values=sample_size_order_CD,
            formats=formats,
            group_col_width=16
        )

        st_number += 1

    # --------------------------------------------------------
    # ST7-ST9: Coverage/type I error/power, Scenarios A/B
    # --------------------------------------------------------
    for c_value in confounding_values:
        table = build_coverage_ab_table(coverage_df, c_value)

        write_coverage_sheet(
            workbook=workbook,
            sheet_name=f"ST{st_number}",
            table=table,
            title_text=(
                f"Supplementary Table {st_number}: Coverage, type I error, and power "
                f"for Scenarios A and B (c_x = c_y = {c_value})"
            ),
            group_header="Instrument Strength",
            scenario_left="Scenario A",
            scenario_right="Scenario B",
            note_text=(
                "Note. Scenario A corresponds to beta_1 = 0, and Scenario B corresponds "
                "to beta_1 = 1. Both scenarios use sample size N = 1000. For the null "
                "scenario, the second operating characteristic is type I error. For the "
                "alternative scenario, the second operating characteristic is power. Tables "
                "are stratified by confounding strength c_x = c_y."
            ),
            group_values=iv_order,
            formats=formats,
            group_col_width=22
        )

        st_number += 1

    # --------------------------------------------------------
    # ST10-ST12: Coverage/type I error/power, Scenarios C/D
    # --------------------------------------------------------
    for c_value in confounding_values:
        table = build_coverage_cd_table(coverage_df, c_value)

        write_coverage_sheet(
            workbook=workbook,
            sheet_name=f"ST{st_number}",
            table=table,
            title_text=(
                f"Supplementary Table {st_number}: Coverage, type I error, and power "
                f"for Scenarios C and D (c_x = c_y = {c_value})"
            ),
            group_header="Sample Size",
            scenario_left="Scenario C",
            scenario_right="Scenario D",
            note_text=(
                "Note. Scenario C corresponds to beta_1 = 0, and Scenario D corresponds "
                "to beta_1 = 1. Both scenarios use weak IVs and vary the sample size. For "
                "the null scenario, the second operating characteristic is type I error. "
                "For the alternative scenario, the second operating characteristic is power. "
                "Tables are stratified by confounding strength c_x = c_y."
            ),
            group_values=sample_size_order_CD,
            formats=formats,
            group_col_width=16
        )

        st_number += 1

    # --------------------------------------------------------
    # ST13-ST15: First-stage F-statistic summaries, Scenarios A/B
    # --------------------------------------------------------
    for c_value in confounding_values:
        table = build_f_ab_table(f_df, c_value)

        write_f_sheet(
            workbook=workbook,
            sheet_name=f"ST{st_number}",
            table=table,
            title_text=(
                f"Supplementary Table {st_number}: First-stage F-statistic summaries "
                f"for Scenarios A and B (c_x = c_y = {c_value})"
            ),
            group_header="Instrument Strength",
            scenario_left="Scenario A",
            scenario_right="Scenario B",
            note_text=(
                "Note. Scenario A corresponds to beta_1 = 0, and Scenario B corresponds "
                "to beta_1 = 1. Both scenarios use sample size N = 1000. First-stage "
                "F-statistic summaries are reported as median (Q1, Q3) for McFadden, "
                "Cox-Snell, and Nagelkerke pseudo-R2-based F summaries. These first-stage "
                "summaries are design-level quantities and do not vary by MR estimation "
                "method. Tables are stratified by confounding strength c_x = c_y."
            ),
            group_values=iv_order,
            formats=formats,
            group_col_width=22
        )

        st_number += 1

    # --------------------------------------------------------
    # ST16-ST18: First-stage F-statistic summaries, Scenarios C/D
    # --------------------------------------------------------
    for c_value in confounding_values:
        table = build_f_cd_table(f_df, c_value)

        write_f_sheet(
            workbook=workbook,
            sheet_name=f"ST{st_number}",
            table=table,
            title_text=(
                f"Supplementary Table {st_number}: First-stage F-statistic summaries "
                f"for Scenarios C and D (c_x = c_y = {c_value})"
            ),
            group_header="Sample Size",
            scenario_left="Scenario C",
            scenario_right="Scenario D",
            note_text=(
                "Note. Scenario C corresponds to beta_1 = 0, and Scenario D corresponds "
                "to beta_1 = 1. Both scenarios use weak IVs and vary the sample size. "
                "First-stage F-statistic summaries are reported as median (Q1, Q3) for "
                "McFadden, Cox-Snell, and Nagelkerke pseudo-R2-based F summaries. These "
                "first-stage summaries are design-level quantities and do not vary by MR "
                "estimation method. Tables are stratified by confounding strength c_x = c_y."
            ),
            group_values=sample_size_order_CD,
            formats=formats,
            group_col_width=16
        )

        st_number += 1


print(f"Saved consolidated supplementary workbook to: {output_file}")
print("Created sheets ST1 through ST18.")