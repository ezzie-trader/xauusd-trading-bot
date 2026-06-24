# XAUUSD Trading Bot - Quick Start Guide

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- MetaTrader 5 installed and running
- Trading account with supported brokers (Just Markets, HFM, or Windsor)

### 2. Installation

```bash
git clone https://github.com/ezzie-trader/xauusd-trading-bot.git
cd xauusd-trading-bot

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configuration

Copy and edit `config.example.json` to `config.json`:

```bash
cp config.example.json config.json
```

Edit `config.json` with your broker credentials:

```json
{
  "broker": {
    "name": "hfm",
    "server": "HotForex-Demo",
    "login": "YOUR_LOGIN",
    "password": "YOUR_PASSWORD"
  }
}
```

### 4. Run the Bot

```bash
python main.py config.json
```

## Strategy Features

### SMC/ICT Analysis
- Order Block Identification
- Breaker Block Analysis
- Fair Value Gaps (FVG)
- Liquidity Pool Detection
- Supply/Demand Zones

### Breakout & Retest
- Key level identification
- Breakout confirmation with volume
- Retest zone analysis
- Entry confirmation

### Risk Management
- Automatic position sizing
- Stop loss and take profit calculation
- Maximum concurrent trades limit
- Margin level monitoring

## Supported Brokers

| Broker | Demo Server |
|--------|-------------|
| Just Markets | JustMarkets-Demo |
| HFM (HotForex) | HotForex-Demo |
| Windsor Brokers | WindsorBrokers-Demo |

## Important Notes

⚠️ **Always test on demo account first!**

- Past performance does not guarantee future results
- Trading carries significant risk
- Only risk money you can afford to lose
- Use proper risk management

## Logs

All activity is logged to `logs/trading_bot.log`

For more details, see README.md
