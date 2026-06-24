import json
import sys
from src.trading_bot import XAUUSDTradingBot


def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    print(f"Loading configuration from {config_file}")
    bot = XAUUSDTradingBot(config_file)
    
    try:
        print("Starting XAUUSD Trading Bot...")
        bot.run()
    except KeyboardInterrupt:
        print("\n\nShutting down trading bot...")
        bot.stop()
    except Exception as e:
        print(f"Error: {str(e)}")
        bot.disconnect()


if __name__ == "__main__":
    main()
