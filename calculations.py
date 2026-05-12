from datetime import datetime
from typing import Dict, List

from models import CallInputRow, MergedGEXRow, PutInputRow, SummaryRow
from settings import PIP_SCALAR


def calculate_gex(gamma: float, contract_size: int, open_interest: int, futures_price: float, option_type: str) -> float:
    direction = 1 if option_type.lower() == "call" else -1
    return gamma * contract_size * open_interest * futures_price * PIP_SCALAR * direction


def build_merged_gex_rows(
    call_rows: List[CallInputRow],
    put_rows: List[PutInputRow],
    futures_price: float,
    contract_size: int,
) -> List[MergedGEXRow]:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    call_by_strike: Dict[float, CallInputRow] = {round(row.strike, 10): row for row in call_rows}
    put_by_strike: Dict[float, PutInputRow] = {round(row.strike, 10): row for row in put_rows}

    all_strikes = sorted(set(call_by_strike.keys()) | set(put_by_strike.keys()))

    merged_rows: List[MergedGEXRow] = []

    for strike in all_strikes:
        call_row = call_by_strike.get(strike)
        put_row = put_by_strike.get(strike)

        call_iv = call_row.volatility if call_row else 0.0
        call_gamma = call_row.gamma if call_row else 0.0
        call_oi = call_row.open_interest if call_row else 0
        call_gex = (
            calculate_gex(call_gamma, contract_size, call_oi, futures_price, "call")
            if call_row else 0.0
        )

        put_iv = put_row.volatility if put_row else 0.0
        put_gamma = put_row.gamma if put_row else 0.0
        put_oi = put_row.open_interest if put_row else 0
        put_gex = (
            calculate_gex(put_gamma, contract_size, put_oi, futures_price, "put")
            if put_row else 0.0
        )

        net_gex = call_gex + put_gex

        merged_rows.append(
            MergedGEXRow(
                timestamp=timestamp,
                strike=strike,
                call_iv=call_iv,
                call_gamma=call_gamma,
                call_oi=call_oi,
                call_gex=call_gex,
                put_iv=put_iv,
                put_gamma=put_gamma,
                put_oi=put_oi,
                put_gex=put_gex,
                net_gex=net_gex,
                futures_price=futures_price,
            )
        )

    return merged_rows


def build_summary_row(merged_rows: List[MergedGEXRow], futures_price: float) -> SummaryRow:
    if not merged_rows:
        raise ValueError("Cannot build summary row from empty merged_rows")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_call_gex = sum(row.call_gex for row in merged_rows)
    total_put_gex = sum(row.put_gex for row in merged_rows)
    net_total_gex = sum(row.net_gex for row in merged_rows)

    max_positive_row = max(merged_rows, key=lambda row: row.net_gex)
    max_negative_row = min(merged_rows, key=lambda row: row.net_gex)
    largest_absolute_row = max(merged_rows, key=lambda row: abs(row.net_gex))

    return SummaryRow(
        timestamp=timestamp,
        futures_price=futures_price,
        total_call_gex=total_call_gex,
        total_put_gex=total_put_gex,
        net_total_gex=net_total_gex,
        max_positive_strike=max_positive_row.strike,
        max_negative_strike=max_negative_row.strike,
        largest_absolute_gex_strike=largest_absolute_row.strike,
    )
