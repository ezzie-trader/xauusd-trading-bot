import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

class SMCICTAnalyzer:
    """Smart Money Concepts & Inner Circle Trader Strategy Analyzer"""
    
    def __init__(self, config: Dict):
        """Initialize SMC/ICT analyzer"""
        self.config = config
        self.logger = logging.getLogger('smc_ict_analyzer')
        self.order_block_periods = config['strategy'].get('order_block_periods', 5)
        self.fvg_threshold = config['strategy'].get('fvg_threshold', 0.0002)
        self.liquidity_lookback = config['strategy'].get('liquidity_lookback', 20)
    
    def identify_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """Identify order blocks (institutional support/resistance zones)"""
        order_blocks = []
        
        for i in range(self.order_block_periods, len(df) - 1):
            if (df['close'].iloc[i-self.order_block_periods:i].min() < df['close'].iloc[i] and
                df['high'].iloc[i-self.order_block_periods:i].max() < df['high'].iloc[i]):
                
                order_blocks.append({
                    'type': 'bullish',
                    'high': df['high'].iloc[i],
                    'low': df['low'].iloc[i],
                    'index': i,
                    'time': df.index[i],
                    'strength': self._calculate_block_strength(df, i, 'bullish')
                })
            
            elif (df['close'].iloc[i-self.order_block_periods:i].max() > df['close'].iloc[i] and
                  df['low'].iloc[i-self.order_block_periods:i].min() > df['low'].iloc[i]):
                
                order_blocks.append({
                    'type': 'bearish',
                    'high': df['high'].iloc[i],
                    'low': df['low'].iloc[i],
                    'index': i,
                    'time': df.index[i],
                    'strength': self._calculate_block_strength(df, i, 'bearish')
                })
        
        return order_blocks
    
    def _calculate_block_strength(self, df: pd.DataFrame, index: int, block_type: str) -> float:
        """Calculate strength of order block"""
        try:
            volume_avg = df['volume'].iloc[max(0, index-10):index].mean()
            current_volume = df['volume'].iloc[index]
            volume_strength = min(current_volume / volume_avg, 2.0) if volume_avg > 0 else 1.0
            
            if block_type == 'bullish':
                momentum = (df['close'].iloc[index] - df['open'].iloc[index]) / (df['high'].iloc[index] - df['low'].iloc[index] + 1e-10)
            else:
                momentum = (df['open'].iloc[index] - df['close'].iloc[index]) / (df['high'].iloc[index] - df['low'].iloc[index] + 1e-10)
            
            return min((abs(momentum) * volume_strength), 2.0)
        except:
            return 1.0
    
    def identify_breaker_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """Identify breaker blocks (break and retest levels)"""
        breaker_blocks = []
        
        for i in range(self.order_block_periods + 5, len(df) - 1):
            prev_high = df['high'].iloc[max(0, i-self.order_block_periods):i].max()
            if df['low'].iloc[i] > prev_high and df['close'].iloc[i] < df['open'].iloc[i]:
                breaker_blocks.append({
                    'type': 'bullish',
                    'level': prev_high,
                    'index': i,
                    'time': df.index[i],
                    'current_price': df['close'].iloc[i]
                })
            
            prev_low = df['low'].iloc[max(0, i-self.order_block_periods):i].min()
            if df['high'].iloc[i] < prev_low and df['close'].iloc[i] > df['open'].iloc[i]:
                breaker_blocks.append({
                    'type': 'bearish',
                    'level': prev_low,
                    'index': i,
                    'time': df.index[i],
                    'current_price': df['close'].iloc[i]
                })
        
        return breaker_blocks
    
    def identify_fair_value_gaps(self, df: pd.DataFrame) -> List[Dict]:
        """Identify Fair Value Gaps (FVG)"""
        fvgs = []
        
        for i in range(1, len(df) - 1):
            gap_size = abs(df['high'].iloc[i] - df['low'].iloc[i-1]) / df['close'].iloc[i]
            
            if df['low'].iloc[i] > df['high'].iloc[i-1] and gap_size > self.fvg_threshold:
                fvgs.append({
                    'type': 'bullish',
                    'gap_low': df['high'].iloc[i-1],
                    'gap_high': df['low'].iloc[i],
                    'index': i,
                    'time': df.index[i],
                    'gap_size': gap_size
                })
            
            elif df['high'].iloc[i] < df['low'].iloc[i-1] and gap_size > self.fvg_threshold:
                fvgs.append({
                    'type': 'bearish',
                    'gap_high': df['low'].iloc[i-1],
                    'gap_low': df['high'].iloc[i],
                    'index': i,
                    'time': df.index[i],
                    'gap_size': gap_size
                })
        
        return fvgs
    
    def identify_liquidity_pools(self, df: pd.DataFrame) -> List[Dict]:
        """Identify liquidity pools"""
        pools = []
        recent_data = df.iloc[-self.liquidity_lookback:]
        
        swing_high = recent_data['high'].max()
        swing_high_idx = recent_data['high'].idxmax()
        pools.append({
            'type': 'resistance',
            'level': swing_high,
            'time': swing_high_idx,
            'strength': 'high'
        })
        
        swing_low = recent_data['low'].min()
        swing_low_idx = recent_data['low'].idxmin()
        pools.append({
            'type': 'support',
            'level': swing_low,
            'time': swing_low_idx,
            'strength': 'high'
        })
        
        return pools
    
    def analyze_market_structure(self, df: pd.DataFrame) -> Dict:
        """Comprehensive market structure analysis"""
        return {
            'order_blocks': self.identify_order_blocks(df),
            'breaker_blocks': self.identify_breaker_blocks(df),
            'fair_value_gaps': self.identify_fair_value_gaps(df),
            'liquidity_pools': self.identify_liquidity_pools(df)
        }
