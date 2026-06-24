import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

class BreakoutRetestAnalyzer:
    """Breakout and Retest Strategy Analyzer"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger('breakout_retest_analyzer')
        self.breakout_threshold = config['strategy'].get('breakout_threshold', 0.0005)
        self.retest_tolerance = config['strategy'].get('retest_tolerance', 0.0003)
        self.lookback_period = 20
    
    def identify_key_levels(self, df: pd.DataFrame) -> Dict[str, float]:
        """Identify key resistance and support levels"""
        recent_data = df.iloc[-self.lookback_period:]
        
        return {
            'resistance': recent_data['high'].max(),
            'support': recent_data['low'].min(),
            'resistance_index': recent_data['high'].idxmax(),
            'support_index': recent_data['low'].idxmin(),
        }
    
    def detect_breakout(self, df: pd.DataFrame, key_levels: Dict) -> Optional[Dict]:
        """Detect breakout from key levels"""
        current_close = df['close'].iloc[-1]
        current_high = df['high'].iloc[-1]
        current_low = df['low'].iloc[-1]
        current_open = df['open'].iloc[-1]
        
        resistance = key_levels['resistance']
        support = key_levels['support']
        
        if current_close > resistance and (current_close - resistance) / resistance > self.breakout_threshold:
            momentum = self._calculate_momentum(df, 5)
            volume_confirmation = self._check_volume_confirmation(df)
            
            return {
                'type': 'bullish',
                'level': resistance,
                'breakout_price': current_close,
                'breakout_strength': (current_close - resistance) / resistance,
                'momentum': momentum,
                'volume_confirmed': volume_confirmation,
                'time': df.index[-1],
                'candle_body_size': (current_close - current_open) / (current_high - current_low + 1e-10)
            }
        
        elif current_close < support and (support - current_close) / support > self.breakout_threshold:
            momentum = self._calculate_momentum(df, 5)
            volume_confirmation = self._check_volume_confirmation(df)
            
            return {
                'type': 'bearish',
                'level': support,
                'breakout_price': current_close,
                'breakout_strength': (support - current_close) / support,
                'momentum': momentum,
                'volume_confirmed': volume_confirmation,
                'time': df.index[-1],
                'candle_body_size': (current_open - current_close) / (current_high - current_low + 1e-10)
            }
        
        return None
    
    def analyze_breakout_retest(self, df: pd.DataFrame) -> Dict:
        """Comprehensive breakout and retest analysis"""
        key_levels = self.identify_key_levels(df)
        breakout = self.detect_breakout(df, key_levels)
        
        analysis = {
            'key_levels': key_levels,
            'breakout': breakout,
            'retest': None,
            'entry_signal': None
        }
        
        if breakout and self.is_valid_breakout(breakout):
            analysis['entry_signal'] = {
                'type': 'breakout_retest',
                'direction': 'long' if breakout['type'] == 'bullish' else 'short',
                'entry_level': breakout['level'],
                'breakout_level': breakout['level'],
                'confidence': self._calculate_confidence(breakout)
            }
        
        return analysis
    
    def is_valid_breakout(self, breakout: Dict) -> bool:
        """Validate breakout quality"""
        checks = [
            breakout['breakout_strength'] > self.breakout_threshold,
            breakout['volume_confirmed'],
            abs(breakout['momentum']) > 0.001
        ]
        return all(checks)
    
    def _calculate_momentum(self, df: pd.DataFrame, period: int = 5) -> float:
        """Calculate momentum using rate of change"""
        if len(df) < period + 1:
            return 0.0
        
        current_close = df['close'].iloc[-1]
        past_close = df['close'].iloc[-period-1]
        
        if past_close == 0:
            return 0.0
        
        return (current_close - past_close) / past_close
    
    def _check_volume_confirmation(self, df: pd.DataFrame) -> bool:
        """Check if breakout has volume confirmation"""
        if 'volume' not in df.columns or len(df) < 2:
            return True
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].iloc[-20:].mean()
        
        return current_volume > avg_volume * 1.2
    
    def _calculate_confidence(self, breakout: Dict) -> float:
        """Calculate overall confidence score"""
        factors = [
            min(breakout['breakout_strength'] / 0.001, 1.0),
            1.0 if breakout['volume_confirmed'] else 0.5,
            min(abs(breakout['momentum']), 1.0)
        ]
        return sum(factors) / len(factors)
