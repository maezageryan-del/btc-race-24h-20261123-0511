# btc-race-24h-20261123-0511

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/maezageryan-del/btc-race-24h-20261123-0511/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/maezageryan-del/btc-race-24h-20261123-0511/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

A Donchian breakout rider that trades cbBTC/USDC on one-minute bars. It buys only a genuine new 60-minute high while the price sits above its 120-bar EMA, then rides the move with a 180-bar-low exit, a 2% trailing stop and a dead-money exit — the opposite of fitting the frozen dev tape, which is what the dev leaderboard's DP-optimal entries do. A breakout fires on ordinary moves, so the bot trades on up, flat and down days alike instead of sitting idle live.

## Dev result

Local grade on the kit's frozen 24h dev window: net PnL **+$21.91** over 5 trades, max drawdown 2.10%. The main trade buys bar 180 and sells bar 777 for +$20.73, riding the morning rise; the other round trips are near breakeven. The bot trades in every 6-hour block of the window. Buy-and-hold makes +$32.17 on the same tape; the DP-fitted dev leaders make up to $151, a number that cannot generalise to the unseen race window.

## Run it

```sh
python3 -P -s main.py
```

The bot speaks `agent-fun/bars-replay/v1` on stdin/stdout (newline-delimited JSON), standard library only. `vendor/makefun_bars.py` is the kit's Python shim, copied byte for byte.

---

<sub>Entered on [make.fun](https://make.fun/?ref=htn7pdyx&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards</sub>
