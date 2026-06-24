import logging
from typing import Dict, Optional
from datetime import datetime

class RiskManager:
    """Manages risk and position sizing"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.account_risk_percent = config['risk_management'].get('account_risk_percent', 2)
        self.position_size_percent = config['risk_management'].get('position_size_percent', 1)
        self.max_concurrent_trades = config['risk_management'].get('max_concurrent_trades', 2)
        self.default_sl_pips = config['risk_management'].get('stop_loss_pips', 50)
        self.default_tp_pips = config['risk_management'].get('take_profit_pips', 100)
        self.logger = logging.getLogger('risk_manager')
    
    def calculate_position_size(self, account_balance: float, entry_price: float,
                               stop_loss_price: float, symbol_point: float) -> float:
        """Calculate position size based on account balance and risk"""
        try:
            risk_amount = account_balance * (self.account_risk_percent / 100)
            stop_loss_pips = abs(entry_price - stop_loss_price) / symbol_point
            
            if stop_loss_pips <= 0:
                self.logger.warning("Invalid stop loss distance")
                return 0
            
            position_size = risk_amount / (stop_loss_pips * symbol_point)
            max_position = account_balance * (self.position_size_percent / 100)
            position_size = min(position_size, max_position)
            
            return round(position_size, 2)
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0
    
    def calculate_stop_loss(self, entry_price: float, direction: str, 
                           symbol_point: float, custom_pips: Optional[float] = None) -> float:
        """Calculate stop loss price"""
        pips = custom_pips if custom_pips else self.default_sl_pips
        pip_value = pips * symbol_point
        
        if direction == 'long':
            return entry_price - pip_value
        else:
            return entry_price + pip_value
    
    def validate_trade(self, trade_request: Dict, account_info: Dict, 
                      open_positions: list) -> Dict:
        """Validate trade before execution"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if len(open_positions) >= self.max_concurrent_trades:
            validation['is_valid'] = False
            validation['errors'].append(
                f"Maximum concurrent trades ({self.max_concurrent_trades}) reached"
            )
        
        return validation
    
    def get_portfolio_metrics(self, account_info: Dict, open_positions: list) -> Dict:
        """Calculate overall portfolio metrics"""
        total_pnl = sum(p.get('profit', 0) for p in open_positions)
        
        return {
            'balance': account_info['balance'],
            'equity': account_info['equity'],
            'free_margin': account_info['free_margin'],
            'margin_level': account_info['margin_level'],
            'total_pnl': round(total_pnl, 2),
            'pnl_percent': round((total_pnl / account_info['balance'] * 100), 2) if account_info['balance'] > 0 else 0,
            'open_positions': len(open_positions),
            'max_positions': self.max_concurrent_trades
        }
