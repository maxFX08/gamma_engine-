CREDENTIALS_FILE = "service_account.json"
SPREADSHEET_ID = "1j6qIFC-_15yyrm6wcZQD4Iuo-hi18b9ciR3P65HW-xg"

CALL_INPUT_TAB = "Call_Input"
PUT_INPUT_TAB = "Put_Input"
CONFIG_TAB = "Config"
PER_STRIKE_TAB = "Per_Strike_GEX"
SUMMARY_TAB = "Summary"

CALL_INPUT_HEADERS = [
    "volatility",
    "strike",
    "call_price",
    "delta",
    "gamma",
    "vega",
    "theta",
    "open_interest",
]

PUT_INPUT_HEADERS = [
    "volatility",
    "strike",
    "put_price",
    "delta",
    "gamma",
    "vega",
    "theta",
    "open_interest",
]

CONFIG_HEADERS = ["key", "value"]

REQUIRED_CONFIG_KEYS = [
    "futures_price",
    "contract_size",
]

EXPECTED_CONTRACT_SIZE = 125000
PIP_SCALAR = 0.0001
