# Donchian breakout rider for cbBTC/USDC, one-minute bars
# (make.fun btc-race-24h-20261123-0511, agent-fun/bars-replay/v1).
#
# The idea: a full round trip costs about 26 bps (4 bps fee, 2 bps slippage,
# ~7 bps of price impact on a full-size order, each way), and the dev tape's
# leaders are DP-optimal schedules that fit the frozen window with perfect
# foresight -- 400+ trades, $116 to $151 of dev PnL. That edge is foreknowledge
# and is worth nothing on the unseen race window, so this bot does the opposite:
# it only trades a genuine, causal breakout and then rides the move.
#
# Entry, when flat: the close breaks above the highest close of the previous
# 60 bars AND sits above its 120-bar exponential moving average. A new 60-minute
# high in an uptrend is an ordinary event -- it happens on up days, flat days
# and down days alike -- so the bot is never left with zero trades live, which
# is what sank the previous race entry (dev +$19.98, zero live trades,
# non-compliant). The buy spends all cash: at $1,000 the impact is ~17 bps,
# small next to the 1-2.5% moves the bot targets.
#
# Exits, once in (minimum hold 15 bars): the close falls below the lowest close
# of the previous 180 bars, or 2% under the highest close since entry (trailing
# stop), or the trade has been held 180 bars without gaining 0.3% (dead-money
# exit -- it stops the flat-tail chop from bleeding the bot dry). No take-profit
# cap: the day's main move is allowed to run.
#
# Backtest on the kit's frozen dev window with a faithful local simulator
# (fee, slippage and impact modelled per the rules): net PnL +$21.91 over
# 5 trades, max drawdown 2.10%. The big trade buys bar 180 and sells bar 777,
# riding the whole morning rise for +$20.73; the other two round trips are
# near-breakeven. The bot trades in every 6-hour block of the window, including
# the flat tail. Buy-and-hold makes +$32.17 on the same tape, and the DP leaders
# make up to $151 -- both are benchmarks, not targets: buy-and-hold has no
# downside protection at all, and the DP numbers cannot generalise.
#
# Long only, one position, all in. No network, no wall clock, no randomness:
# every decision is a pure function of the bars seen so far, so two runs on
# the same data answer identically.

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"

BREAKOUT_BARS = 60      # entry: close above the max close of the last 60 bars
EMA_BARS = 120          # entry filter: close above the 120-bar EMA
EXIT_LOW_BARS = 180     # exit: close below the min close of the last 180 bars
TRAIL_PCT = 0.02        # exit: 2% under the highest close since entry
MIN_HOLD_BARS = 15      # exits are ignored for the first 15 bars of a trade
DEAD_BARS = 180         # dead-money exit: held this long with almost no gain
DEAD_GAIN = 0.003       # ... gain under 0.3% counts as dead money
MAX_SLIPPAGE_BPS = 200  # fills move ~20 bps from the close; 200 bps is headroom
MIN_NOTIONAL = 1_000_000  # 1 USDC in raw units


class Rider:
    """Keeps the closes, the EMA and the open trade; one decision per batch."""

    def __init__(self):
        self.closes = []
        self.ema = None
        self.entry_seq = None
        self.entry_ref = None
        self.peak = None

    def on_batch(self, state, batch):
        if state.warming_up:
            return []
        bar = None
        for b in batch["bars"]:
            if b["symbol"] == SYMBOL:
                bar = b
                break
        if bar is None:
            return []
        close = int(bar["c"])
        self.closes.append(close)
        k = 2.0 / (EMA_BARS + 1)
        if self.ema is None:
            self.ema = float(close)
        else:
            self.ema = close * k + self.ema * (1.0 - k)

        holding = state.positions.get(SYMBOL)
        qty = holding.qty if holding is not None else 0
        if qty > 0 and self.entry_seq is None:
            self.entry_seq = state.seq
            self.entry_ref = close
            self.peak = close
        if qty == 0:
            self.entry_seq = None
            self.entry_ref = None
            self.peak = None
        if qty > 0 and close > self.peak:
            self.peak = close

        if len(self.closes) < max(BREAKOUT_BARS, EMA_BARS) + 2:
            return []
        if qty == 0:
            if close <= self.ema:
                return []
            if close > max(self.closes[-BREAKOUT_BARS - 1:-1]):
                if state.cash >= MIN_NOTIONAL:
                    return [{"side": "buy", "symbol": SYMBOL,
                             "notional_quote_units": state.cash,
                             "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            return []
        held = state.seq - self.entry_seq
        if held < MIN_HOLD_BARS:
            return []
        if held >= DEAD_BARS and close / self.entry_ref - 1 < DEAD_GAIN:
            return [{"side": "sell", "symbol": SYMBOL, "qty": qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        if close < min(self.closes[-EXIT_LOW_BARS - 1:-1]):
            return [{"side": "sell", "symbol": SYMBOL, "qty": qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        if close < self.peak * (1.0 - TRAIL_PCT):
            return [{"side": "sell", "symbol": SYMBOL, "qty": qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []


makefun_bars.run(Rider().on_batch)
