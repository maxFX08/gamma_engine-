from calculations import build_merged_gex_rows, build_summary_row
from sheets_service import SheetsService
from settings import (
    CALL_INPUT_TAB,
    CONFIG_TAB,
    PER_STRIKE_TAB,
    PUT_INPUT_TAB,
    SUMMARY_TAB,
)
from validators import (
    ValidationError,
    build_missing_strike_warnings,
    parse_call_rows,
    parse_config_records,
    parse_put_rows,
    validate_config_headers,
    validate_input_headers,
    validate_required_tabs,
)


def build_per_strike_output_rows(merged_rows):
    output_rows = []
    for row in merged_rows:
        output_rows.append([
            row.timestamp,
            row.strike,
            row.call_iv,
            row.call_gamma,
            row.call_oi,
            row.call_gex,
            row.put_iv,
            row.put_gamma,
            row.put_oi,
            row.put_gex,
            row.net_gex,
            row.futures_price,
        ])
    return output_rows


def build_summary_output_rows(summary):
    return [[
        summary.timestamp,
        summary.futures_price,
        summary.total_call_gex,
        summary.total_put_gex,
        summary.net_total_gex,
        summary.max_positive_strike,
        summary.max_negative_strike,
        summary.largest_absolute_gex_strike,
    ]]


def main():
    print("=" * 70)
    print("6E GAMMA ENGINE — STAGE 4")
    print("=" * 70)
    print("Connecting to Google Sheets...")

    sheets = SheetsService()

    try:
        sheets.authenticate()
        spreadsheet = sheets.open_spreadsheet()
        print(f"Connected successfully to spreadsheet: {spreadsheet.title}")

        existing_titles = sheets.list_worksheet_titles()
        required_titles = [
            CALL_INPUT_TAB,
            PUT_INPUT_TAB,
            CONFIG_TAB,
            PER_STRIKE_TAB,
            SUMMARY_TAB,
        ]
        validate_required_tabs(existing_titles, required_titles)
        print("All required worksheet tabs are present.")

        call_values = sheets.get_all_values(CALL_INPUT_TAB)
        put_values = sheets.get_all_values(PUT_INPUT_TAB)
        config_values = sheets.get_all_values(CONFIG_TAB)

        if not call_values:
            raise ValidationError("Worksheet 'Call_Input' is empty")
        if not put_values:
            raise ValidationError("Worksheet 'Put_Input' is empty")
        if not config_values:
            raise ValidationError("Worksheet 'Config' is empty")

        call_headers = call_values[0]
        put_headers = put_values[0]
        config_headers = config_values[0]

        validate_input_headers(call_headers, put_headers)
        validate_config_headers(config_headers)

        print("Header validation passed.")

        config_records = sheets.get_all_records(CONFIG_TAB)
        config = parse_config_records(config_records)

        call_records = sheets.get_all_records(CALL_INPUT_TAB)
        put_records = sheets.get_all_records(PUT_INPUT_TAB)

        call_rows = parse_call_rows(call_records)
        put_rows = parse_put_rows(put_records)

        warnings = build_missing_strike_warnings(call_rows, put_rows)

        merged_rows = build_merged_gex_rows(
            call_rows=call_rows,
            put_rows=put_rows,
            futures_price=config["futures_price"],
            contract_size=config["contract_size"],
        )

        summary = build_summary_row(
            merged_rows=merged_rows,
            futures_price=config["futures_price"],
        )

        print("-" * 70)
        print("CONFIG")
        print(f"futures_price: {config['futures_price']}")
        print(f"contract_size: {config['contract_size']}")

        print("-" * 70)
        print("INPUT SUMMARY")
        print(f"Validated call rows: {len(call_rows)}")
        print(f"Validated put rows: {len(put_rows)}")
        print(f"Merged strike rows: {len(merged_rows)}")

        if warnings:
            print("-" * 70)
            print("WARNINGS")
            for warning in warnings:
                print(f"- {warning}")
        else:
            print("-" * 70)
            print("No missing-strike warnings detected.")

        per_strike_output_rows = build_per_strike_output_rows(merged_rows)
        summary_output_rows = build_summary_output_rows(summary)

        print("-" * 70)
        print("Writing results to Google Sheets...")

        sheets.clear_data_rows(PER_STRIKE_TAB, "L")
        sheets.write_rows(PER_STRIKE_TAB, per_strike_output_rows, start_cell="A2")

        sheets.clear_data_rows(SUMMARY_TAB, "H")
        sheets.write_rows(SUMMARY_TAB, summary_output_rows, start_cell="A2")

        sheets.format_headers()
        sheets.format_output_sheets(
            per_strike_row_count=len(per_strike_output_rows),
            summary_row_count=len(summary_output_rows),
        )

        print("Per_Strike_GEX updated successfully.")
        print("Summary updated successfully.")

        print("-" * 70)
        print("SUMMARY")
        print(f"Total Call GEX: {summary.total_call_gex:,.0f}")
        print(f"Total Put GEX: {summary.total_put_gex:,.0f}")
        print(f"Net Total GEX: {summary.net_total_gex:,.0f}")
        print(f"Max Positive Strike: {summary.max_positive_strike:.4f}")
        print(f"Max Negative Strike: {summary.max_negative_strike:.4f}")
        print(f"Largest Absolute GEX Strike: {summary.largest_absolute_gex_strike:.4f}")

        print("=" * 70)
        print("Stage 4 completed successfully.")
        print("Google Sheets outputs have been refreshed.")
        print("=" * 70)

    except ValidationError as exc:
        print("-" * 70)
        print("VALIDATION ERROR")
        print(str(exc))
        print("=" * 70)
    except Exception as exc:
        print("-" * 70)
        print("RUNTIME ERROR")
        print(str(exc))
        print("=" * 70)


if __name__ == "__main__":
    main()
