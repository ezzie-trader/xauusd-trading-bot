import logging
import json
import time
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

from src.broker_connection import BrokerConnection
from src.smc_ict_analyzer import SMCICTAnalyzer
from src.breakout_retest_analyzer import BreakoutRetestAnalyzer
from src.risk_manager import RiskManager


class XAUUSDTradingBot:
    """Main XAUUSD Trading Bot - SMC/ICT + Breakout & Retest Strategy"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.broker = BrokerConnection(self.config)
        self.smc_ict = SMCICTAnalyzer(self.config)
        self.breakout_retest = BreakoutRetestAnalyzer(self.config)
        self.risk_manager = RiskManager(self.config)
        self.running = False
        self.trade_log = []
        
        self.logger.info("Trading bot initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            raise
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('xauusd_bot')
        
        import os
        os.makedirs('logs', exist_ok=True)
        
        handler = logging.FileHandler('logs/trading_bot.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        return logger
    
    def connect(self) -> bool:
        self.logger.info(f"Connecting to {self.config['broker']['name']}...")
        if self.broker.connect():
            self.logger.info("Connected to broker successfully")
            return True
        else:
            self.logger.error("Failed to connect to broker")
            return False
    
    def disconnect(self):
        self.logger.info("Disconnecting from broker...")
        self.broker.disconnect()
        self.logger.info("Disconnected from broker")
    
    def run(self):
        if not self.connect():
            self.logger.error("Failed to connect to broker")
            return
        
        try:
            self.running = True
            self.logger.info("Trading bot started")
            
            timeframes = self.config['strategy'].get('timeframes', ['H1', 'H4', 'D1'])
            
            while self.running:
                try:
                    time.sleep(300)
                except Exception as e:
                    self.logger.error(f"Error in trading loop: {str(e)}")
                    time.sleep(60)
        
        finally:
            self.disconnect()
            self.logger.info("Trading bot stopped")
    
    def stop(self):
        self.running = False
        self.logger.info("Stop signal received")


if __name__ == "__main__":
    import sys
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    bot = XAUUSDTradingBot(config_file)
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        bot.stop()
