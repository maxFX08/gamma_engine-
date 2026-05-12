from dataclasses import dataclass


@dataclass
class CallInputRow:
    volatility: float
    strike: float
    call_price: float
    delta: float
    gamma: float
    vega: float
    theta: float
    open_interest: int


@dataclass
class PutInputRow:
    volatility: float
    strike: float
    put_price: float
    delta: float
    gamma: float
    vega: float
    theta: float
    open_interest: int


@dataclass
class MergedGEXRow:
    timestamp: str
    strike: float
    call_iv: float
    call_gamma: float
    call_oi: int
    call_gex: float
    put_iv: float
    put_gamma: float
    put_oi: int
    put_gex: float
    net_gex: float
    futures_price: float


@dataclass
class SummaryRow:
    timestamp: str
    futures_price: float
    total_call_gex: float
    total_put_gex: float
    net_total_gex: float
    max_positive_strike: float
    max_negative_strike: float
    largest_absolute_gex_strike: float
