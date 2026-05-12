from typing import Dict, List, Sequence, Tuple

from models import CallInputRow, PutInputRow
from settings import (
    CALL_INPUT_HEADERS,
    CONFIG_HEADERS,
    EXPECTED_CONTRACT_SIZE,
    REQUIRED_CONFIG_KEYS,
    PUT_INPUT_HEADERS,
)


class ValidationError(Exception):
    """Raised when workbook structure or input data is invalid."""


def normalize_header_row(header_row: Sequence[str]) -> List[str]:
    return [str(cell).strip() for cell in header_row]


def normalize_record_keys(record: Dict) -> Dict[str, str]:
    normalized = {}
    for key, value in record.items():
        normalized[str(key).strip()] = value
    return normalized


def is_blank_record(record: Dict) -> bool:
    return all(str(value).strip() == "" for value in record.values())


def validate_required_tabs(existing_titles: List[str], required_titles: List[str]) -> None:
    missing = [title for title in required_titles if title not in existing_titles]
    if missing:
        raise ValidationError(f"Missing required worksheet tabs: {', '.join(missing)}")


def validate_headers(actual_headers: Sequence[str], expected_headers: Sequence[str], worksheet_name: str) -> None:
    normalized_actual = normalize_header_row(actual_headers)
    normalized_expected = list(expected_headers)

    if normalized_actual != normalized_expected:
        raise ValidationError(
            f"Header mismatch in '{worksheet_name}'. "
            f"Expected {normalized_expected}, got {normalized_actual}"
        )


def validate_config_headers(actual_headers: Sequence[str]) -> None:
    validate_headers(actual_headers, CONFIG_HEADERS, "Config")


def parse_config_records(records: List[Dict]) -> Dict[str, str]:
    config = {}

    for raw_record in records:
        record = normalize_record_keys(raw_record)
        if is_blank_record(record):
            continue

        key = str(record.get("key", "")).strip()
        value = str(record.get("value", "")).strip()

        if key:
            config[key] = value

    missing_keys = [key for key in REQUIRED_CONFIG_KEYS if key not in config]
    if missing_keys:
        raise ValidationError(f"Missing required config keys: {', '.join(missing_keys)}")

    futures_price_raw = config.get("futures_price", "").strip()
    contract_size_raw = config.get("contract_size", "").strip()

    if futures_price_raw == "":
        raise ValidationError("Config value 'futures_price' is blank")

    try:
        futures_price = float(futures_price_raw)
    except ValueError:
        raise ValidationError(f"Config value 'futures_price' must be numeric, got '{futures_price_raw}'")

    try:
        contract_size = int(float(contract_size_raw))
    except ValueError:
        raise ValidationError(f"Config value 'contract_size' must be numeric, got '{contract_size_raw}'")

    if futures_price <= 0:
        raise ValidationError("Config value 'futures_price' must be greater than 0")

    if contract_size != EXPECTED_CONTRACT_SIZE:
        raise ValidationError(
            f"Config value 'contract_size' must be {EXPECTED_CONTRACT_SIZE}, got {contract_size}"
        )

    return {
        "futures_price": futures_price,
        "contract_size": contract_size,
    }


def _parse_float(value, field_name: str, row_number: int, worksheet_name: str) -> float:
    raw = str(value).strip()
    if raw == "":
        raise ValidationError(
            f"Blank value for '{field_name}' in worksheet '{worksheet_name}' row {row_number}"
        )
    try:
        return float(raw)
    except ValueError:
        raise ValidationError(
            f"Invalid numeric value for '{field_name}' in worksheet '{worksheet_name}' row {row_number}: '{raw}'"
        )


def _parse_int(value, field_name: str, row_number: int, worksheet_name: str) -> int:
    raw = str(value).strip()
    if raw == "":
        raise ValidationError(
            f"Blank value for '{field_name}' in worksheet '{worksheet_name}' row {row_number}"
        )
    try:
        parsed = int(float(raw))
    except ValueError:
        raise ValidationError(
            f"Invalid integer value for '{field_name}' in worksheet '{worksheet_name}' row {row_number}: '{raw}'"
        )
    return parsed


def parse_call_rows(records: List[Dict]) -> List[CallInputRow]:
    parsed_rows: List[CallInputRow] = []
    seen_strikes = set()

    for index, raw_record in enumerate(records, start=2):
        record = normalize_record_keys(raw_record)

        if is_blank_record(record):
            continue

        row = CallInputRow(
            volatility=_parse_float(record.get("volatility", ""), "volatility", index, "Call_Input"),
            strike=_parse_float(record.get("strike", ""), "strike", index, "Call_Input"),
            call_price=_parse_float(record.get("call_price", ""), "call_price", index, "Call_Input"),
            delta=_parse_float(record.get("delta", ""), "delta", index, "Call_Input"),
            gamma=_parse_float(record.get("gamma", ""), "gamma", index, "Call_Input"),
            vega=_parse_float(record.get("vega", ""), "vega", index, "Call_Input"),
            theta=_parse_float(record.get("theta", ""), "theta", index, "Call_Input"),
            open_interest=_parse_int(record.get("open_interest", ""), "open_interest", index, "Call_Input"),
        )

        if row.open_interest < 0:
            raise ValidationError(f"Negative open_interest in Call_Input row {index}")

        if row.gamma < 0:
            raise ValidationError(f"Negative gamma in Call_Input row {index}")

        strike_key = round(row.strike, 10)
        if strike_key in seen_strikes:
            raise ValidationError(f"Duplicate strike {row.strike} found in Call_Input")
        seen_strikes.add(strike_key)

        parsed_rows.append(row)

    return parsed_rows


def parse_put_rows(records: List[Dict]) -> List[PutInputRow]:
    parsed_rows: List[PutInputRow] = []
    seen_strikes = set()

    for index, raw_record in enumerate(records, start=2):
        record = normalize_record_keys(raw_record)

        if is_blank_record(record):
            continue

        row = PutInputRow(
            volatility=_parse_float(record.get("volatility", ""), "volatility", index, "Put_Input"),
            strike=_parse_float(record.get("strike", ""), "strike", index, "Put_Input"),
            put_price=_parse_float(record.get("put_price", ""), "put_price", index, "Put_Input"),
            delta=_parse_float(record.get("delta", ""), "delta", index, "Put_Input"),
            gamma=_parse_float(record.get("gamma", ""), "gamma", index, "Put_Input"),
            vega=_parse_float(record.get("vega", ""), "vega", index, "Put_Input"),
            theta=_parse_float(record.get("theta", ""), "theta", index, "Put_Input"),
            open_interest=_parse_int(record.get("open_interest", ""), "open_interest", index, "Put_Input"),
        )

        if row.open_interest < 0:
            raise ValidationError(f"Negative open_interest in Put_Input row {index}")

        if row.gamma < 0:
            raise ValidationError(f"Negative gamma in Put_Input row {index}")

        strike_key = round(row.strike, 10)
        if strike_key in seen_strikes:
            raise ValidationError(f"Duplicate strike {row.strike} found in Put_Input")
        seen_strikes.add(strike_key)

        parsed_rows.append(row)

    return parsed_rows


def validate_input_headers(call_headers: Sequence[str], put_headers: Sequence[str]) -> None:
    validate_headers(call_headers, CALL_INPUT_HEADERS, "Call_Input")
    validate_headers(put_headers, PUT_INPUT_HEADERS, "Put_Input")


def build_missing_strike_warnings(
    call_rows: List[CallInputRow],
    put_rows: List[PutInputRow],
) -> List[str]:
    call_strikes = {round(row.strike, 10) for row in call_rows}
    put_strikes = {round(row.strike, 10) for row in put_rows}

    warnings = []

    missing_in_put = sorted(call_strikes - put_strikes)
    missing_in_call = sorted(put_strikes - call_strikes)

    for strike in missing_in_put:
        warnings.append(f"Strike {strike} exists in Call_Input but not Put_Input; put-side will later default to zero")

    for strike in missing_in_call:
        warnings.append(f"Strike {strike} exists in Put_Input but not Call_Input; call-side will later default to zero")

    return warnings
