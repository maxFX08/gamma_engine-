import gspread
from google.oauth2.service_account import Credentials

from settings import (
    CALL_INPUT_TAB,
    CONFIG_TAB,
    CREDENTIALS_FILE,
    PER_STRIKE_TAB,
    PUT_INPUT_TAB,
    SPREADSHEET_ID,
    SUMMARY_TAB,
)


class SheetsService:
    def __init__(self):
        self.client = None
        self.spreadsheet = None

    def authenticate(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=scope,
        )
        self.client = gspread.authorize(credentials)
        return self.client

    def open_spreadsheet(self):
        if self.client is None:
            self.authenticate()
        self.spreadsheet = self.client.open_by_key(SPREADSHEET_ID)
        return self.spreadsheet

    def get_worksheet(self, worksheet_name: str):
        if self.spreadsheet is None:
            self.open_spreadsheet()
        return self.spreadsheet.worksheet(worksheet_name)

    def list_worksheet_titles(self):
        if self.spreadsheet is None:
            self.open_spreadsheet()
        return [ws.title for ws in self.spreadsheet.worksheets()]

    def get_all_values(self, worksheet_name: str):
        worksheet = self.get_worksheet(worksheet_name)
        return worksheet.get_all_values()

    def get_all_records(self, worksheet_name: str):
        worksheet = self.get_worksheet(worksheet_name)
        return worksheet.get_all_records()

    def clear_data_rows(self, worksheet_name: str, end_column_letter: str):
        worksheet = self.get_worksheet(worksheet_name)
        worksheet.batch_clear([f"A2:{end_column_letter}1000"])

    def write_rows(self, worksheet_name: str, rows, start_cell: str = "A2"):
        worksheet = self.get_worksheet(worksheet_name)
        if rows:
            worksheet.update(start_cell, rows)

    def format_headers(self):
        header_format = {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
            "horizontalAlignment": "CENTER",
        }

        self.get_worksheet(CALL_INPUT_TAB).format("A1:H1", header_format)
        self.get_worksheet(PUT_INPUT_TAB).format("A1:H1", header_format)
        self.get_worksheet(CONFIG_TAB).format("A1:B1", header_format)
        self.get_worksheet(PER_STRIKE_TAB).format("A1:L1", header_format)
        self.get_worksheet(SUMMARY_TAB).format("A1:H1", header_format)

    def format_output_sheets(self, per_strike_row_count: int, summary_row_count: int):
        per_strike_ws = self.get_worksheet(PER_STRIKE_TAB)
        summary_ws = self.get_worksheet(SUMMARY_TAB)

        if per_strike_row_count > 0:
            last_row = per_strike_row_count + 1

            per_strike_ws.format(f"B2:B{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "0.0000"}
            })
            per_strike_ws.format(f"C2:C{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "0.00"}
            })
            per_strike_ws.format(f"D2:D{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "0.0000"}
            })
            per_strike_ws.format(f"E2:E{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "0"}
            })
            per_strike_ws.format(f"F2:F{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "#,##0"}
            })
            per_strike_ws.format(f"G2:G{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "0.00"}
            })
            per_strike_ws.format(f"H2:H{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "0.0000"}
            })
            per_strike_ws.format(f"I2:I{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "0"}
            })
            per_strike_ws.format(f"J2:J{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "#,##0"}
            })
            per_strike_ws.format(f"K2:K{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "#,##0"}
            })
            per_strike_ws.format(f"L2:L{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "0.0000"}
            })

            per_strike_ws.format(f"F2:F{last_row}", {
                "backgroundColor": {"red": 0.90, "green": 1.00, "blue": 0.90}
            })
            per_strike_ws.format(f"J2:J{last_row}", {
                "backgroundColor": {"red": 1.00, "green": 0.90, "blue": 0.90}
            })

        if summary_row_count > 0:
            last_row = summary_row_count + 1

            summary_ws.format(f"B2:B{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "0.0000"}
            })
            summary_ws.format(f"C2:E{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "#,##0"}
            })
            summary_ws.format(f"F2:H{last_row}", {
                "numberFormat": {"type": "NUMBER", "pattern": "0.0000"}
            })
