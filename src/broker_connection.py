import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import MetaTrader5 as mt5

class BrokerConnection:
    """Manages connections to different brokers"""
    
    BROKER_SERVERS = {
        'justmarkets': 'JustMarkets-Demo',
        'hfm': 'HotForex-Demo',
        'windsor': 'WindsorBrokers-Demo'
    }
    
    def __init__(self, config: Dict):
        self.config = config
        self.broker_name = config['broker']['name'].lower()
        self.login = config['broker']['login']
        self.password = config['broker']['password']
        self.server = self.BROKER_SERVERS.get(self.broker_name, config['broker'].get('server'))
        self.timeout = config['broker'].get('timeout', 5000)
        self.connected = False
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        logger = logging.getLogger(f'broker_{self.broker_name}')
        os.makedirs('logs', exist_ok=True)
        handler = logging.FileHandler(f'logs/broker_{self.broker_name}.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    
    def connect(self) -> bool:
        """Connect to broker via MetaTrader5"""
        try:
            if not mt5.initialize():
                self.logger.error(f"Failed to initialize MetaTrader5: {mt5.last_error()}")
                return False
            
            authorized = mt5.login(self.login, self.password, self.server)
            if not authorized:
                self.logger.error(f"Failed to login to {self.broker_name}: {mt5.last_error()}")
                return False
            
            self.connected = True
            self.logger.info(f"Successfully connected to {self.broker_name}")
            return True
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        if self.connected:
            mt5.shutdown()
            self.connected = False
            self.logger.info(f"Disconnected from {self.broker_name}")
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return None
            
            return {
                'balance': account_info.balance,
                'equity': account_info.equity,
                'free_margin': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'currency': account_info.currency,
                'login': account_info.login
            }
        except Exception as e:
            self.logger.error(f"Error getting account info: {str(e)}")
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return None
            
            return {
                'ask': symbol_info.ask,
                'bid': symbol_info.bid,
                'point': symbol_info.point,
                'digits': symbol_info.digits,
                'volume_min': symbol_info.volume_min,
                'volume_max': symbol_info.volume_max,
                'volume_step': symbol_info.volume_step
            }
        except Exception as e:
            self.logger.error(f"Error getting symbol info: {str(e)}")
            return None
    
    def get_rates(self, symbol: str, timeframe: str, count: int) -> Optional[List]:
        """Get historical price data"""
        try:
            timeframe_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1,
                'W1': mt5.TIMEFRAME_W1
            }
            
            tf = timeframe_map.get(timeframe)
            if tf is None:
                return None
            
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
            return rates if rates is not None else None
        except Exception as e:
            self.logger.error(f"Error getting rates: {str(e)}")
            return None
    
    def get_positions(self, symbol: str = None) -> Optional[List[Dict]]:
        """Get open positions"""
        try:
            positions = mt5.positions_get(symbol=symbol)
            return positions if positions else []
        except Exception as e:
            self.logger.error(f"Error getting positions: {str(e)}")
            return None
