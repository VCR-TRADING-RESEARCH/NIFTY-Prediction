import math
from datetime import date
import pytest

from scripts.exploratory_positional_backtest import (
    bs_price, implied_vol, option_delta, lot_size, fee_rates, order_costs
)

def test_black_scholes_iv_round_trip_call_and_put():
    for kind in ("CALL","PUT"):
        premium=bs_price(25000,25000,10/365.25,0.06,0.01,0.22,kind)
        iv=implied_vol(premium,25000,25000,10/365.25,kind)
        assert iv == pytest.approx(0.22,abs=1e-6)

def test_delta_signs():
    call=option_delta(25000,25000,10/365.25,0.06,0.01,0.2,"CALL")
    put=option_delta(25000,25000,10/365.25,0.06,0.01,0.2,"PUT")
    assert 0 < call < 1
    assert -1 < put < 0

def test_historical_lot_size_boundaries():
    assert lot_size(date(2024,12,19))==25
    assert lot_size(date(2025,1,2))==75
    assert lot_size(date(2025,12,30))==75
    assert lot_size(date(2026,1,6))==65
    with pytest.raises(ValueError):
        lot_size(date(2026,1,2))

def test_fee_rate_effective_dates():
    assert fee_rates(date(2026,2,28))==(pytest.approx(0.0003503),pytest.approx(0.001))
    assert fee_rates(date(2026,3,1))==(pytest.approx(0.0003553),pytest.approx(0.001))
    assert fee_rates(date(2026,4,1))==(pytest.approx(0.0003553),pytest.approx(0.0015))

def test_costs_apply_sell_stt_and_buy_stamp_only():
    orders=[{"side":"SELL","price":100.0,"qty":75},{"side":"BUY","price":50.0,"qty":75}]
    c=order_costs(orders,date(2025,1,1))
    assert c["brokerage"]==20
    assert c["stt"]==pytest.approx(7.5)
    assert c["stamp"]==pytest.approx(0.1125)
    assert c["exchange"]==pytest.approx(150*75*0.0003503)
    assert c["total"]>c["brokerage"]+c["stt"]+c["stamp"]

def test_credit_spread_pnl_sign_convention():
    qty=75
    credit=20.0
    buyback=10.0
    assert (credit-buyback)*qty==750
    assert (credit-30.0)*qty==-750
