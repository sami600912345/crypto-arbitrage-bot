"""
مدير المخاطر لبرنامج المراجحة
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from config import Config

class RiskManager:
    """مدير المخاطر والأمان"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.trade_history = []
        self.daily_losses = {}
        self.position_sizes = {}
        self.blacklisted_pairs = set()
        self.max_daily_trades = 100
        self.max_daily_loss = 1000  # USDT
        self.cooldown_periods = {}  # فترات التهدئة للأزواج
        
    def validate_opportunity(self, opportunity: Dict) -> Tuple[bool, str]:
        """التحقق من صحة فرصة المراجحة"""
        try:
            # التحقق من الحد الأدنى للربح
            if opportunity['profit_percentage'] < Config.MIN_PROFIT_PERCENTAGE:
                return False, f"نسبة الربح أقل من الحد الأدنى: {opportunity['profit_percentage']:.2f}%"
            
            # التحقق من القائمة السوداء
            if opportunity['symbol'] in self.blacklisted_pairs:
                return False, f"الزوج {opportunity['symbol']} في القائمة السوداء"
            
            # التحقق من فترة التهدئة
            if self._is_in_cooldown(opportunity['symbol']):
                return False, f"الزوج {opportunity['symbol']} في فترة تهدئة"
            
            # التحقق من الحد الأقصى للصفقات اليومية
            today = datetime.now().date()
            daily_trades = len([t for t in self.trade_history 
                              if t['timestamp'].date() == today])
            
            if daily_trades >= self.max_daily_trades:
                return False, "تم الوصول للحد الأقصى للصفقات اليومية"
            
            # التحقق من الخسائر اليومية
            daily_loss = self.daily_losses.get(today, 0)
            if daily_loss >= self.max_daily_loss:
                return False, f"تم الوصول للحد الأقصى للخسائر اليومية: {daily_loss} USDT"
            
            # التحقق من انتشار السعر (Spread)
            spread_percentage = ((opportunity['sell_price'] - opportunity['buy_price']) / 
                               opportunity['buy_price']) * 100
            
            if spread_percentage > 10:  # انتشار أكبر من 10% مشبوه
                return False, f"انتشار السعر مشبوه: {spread_percentage:.2f}%"
            
            return True, "الفرصة صالحة"
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من الفرصة: {e}")
            return False, f"خطأ في التحقق: {str(e)}"
    
    def calculate_position_size(self, opportunity: Dict, available_balance: float) -> float:
        """حساب حجم المركز الآمن"""
        try:
            # الحد الأقصى للمخاطرة لكل صفقة (2% من الرصيد)
            max_risk_per_trade = available_balance * 0.02
            
            # حساب المخاطرة المحتملة (بناءً على الانزلاق المحتمل)
            potential_slippage = Config.MAX_SLIPPAGE / 100
            risk_amount = opportunity['buy_price'] * potential_slippage
            
            # حساب الحد الأقصى للكمية بناءً على المخاطرة
            max_quantity_by_risk = max_risk_per_trade / risk_amount
            
            # الحد الأقصى بناءً على التكوين
            max_by_config = min(Config.MAX_TRADE_AMOUNT, available_balance * 0.1)
            
            # اختيار الأصغر
            position_size = min(
                max_quantity_by_risk,
                max_by_config,
                Config.MAX_TRADE_AMOUNT
            )
            
            # التأكد من الحد الأدنى
            if position_size < Config.MIN_TRADE_AMOUNT:
                return 0
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"خطأ في حساب حجم المركز: {e}")
            return 0
    
    def validate_trade_execution(self, opportunity: Dict, trade_amount: float) -> Tuple[bool, str]:
        """التحقق من صحة تنفيذ الصفقة"""
        try:
            # التحقق من حجم الصفقة
            if trade_amount < Config.MIN_TRADE_AMOUNT:
                return False, f"حجم الصفقة أقل من الحد الأدنى: {trade_amount}"
            
            if trade_amount > Config.MAX_TRADE_AMOUNT:
                return False, f"حجم الصفقة أكبر من الحد الأقصى: {trade_amount}"
            
            # التحقق من نسبة الربح المتوقعة بعد الرسوم
            estimated_fees = self._estimate_trading_fees(opportunity, trade_amount)
            net_profit = (opportunity['profit_amount'] * trade_amount) - estimated_fees
            net_profit_percentage = (net_profit / (opportunity['buy_price'] * trade_amount)) * 100
            
            if net_profit_percentage < Config.MIN_PROFIT_PERCENTAGE:
                return False, f"الربح الصافي أقل من الحد الأدنى بعد الرسوم: {net_profit_percentage:.2f}%"
            
            return True, "الصفقة صالحة للتنفيذ"
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من تنفيذ الصفقة: {e}")
            return False, f"خطأ في التحقق: {str(e)}"
    
    def _estimate_trading_fees(self, opportunity: Dict, trade_amount: float) -> float:
        """تقدير رسوم التداول"""
        # رسوم تقديرية للمنصات المختلفة
        fee_rates = {
            'binance': 0.001,  # 0.1%
            'coinbasepro': 0.005,  # 0.5%
            'kraken': 0.0026,  # 0.26%
            'kucoin': 0.001,  # 0.1%
            'huobi': 0.002  # 0.2%
        }
        
        buy_fee_rate = fee_rates.get(opportunity['buy_exchange'], 0.002)
        sell_fee_rate = fee_rates.get(opportunity['sell_exchange'], 0.002)
        
        buy_fee = opportunity['buy_price'] * trade_amount * buy_fee_rate
        sell_fee = opportunity['sell_price'] * trade_amount * sell_fee_rate
        
        return buy_fee + sell_fee
    
    def record_trade(self, trade_result: Dict):
        """تسجيل نتيجة الصفقة"""
        try:
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': trade_result.get('symbol'),
                'profit': trade_result.get('profit', 0),
                'success': trade_result.get('success', False),
                'buy_exchange': trade_result.get('buy_exchange'),
                'sell_exchange': trade_result.get('sell_exchange'),
                'trade_amount': trade_result.get('trade_amount', 0)
            }
            
            self.trade_history.append(trade_record)
            
            # تحديث الخسائر اليومية
            today = datetime.now().date()
            if trade_record['profit'] < 0:
                if today not in self.daily_losses:
                    self.daily_losses[today] = 0
                self.daily_losses[today] += abs(trade_record['profit'])
            
            # إضافة فترة تهدئة في حالة الخسارة
            if not trade_record['success'] or trade_record['profit'] < 0:
                self._add_cooldown(trade_record['symbol'], minutes=30)
            
            self.logger.info(f"تم تسجيل الصفقة: {trade_record}")
            
        except Exception as e:
            self.logger.error(f"خطأ في تسجيل الصفقة: {e}")
    
    def _is_in_cooldown(self, symbol: str) -> bool:
        """التحقق من فترة التهدئة"""
        if symbol not in self.cooldown_periods:
            return False
        
        cooldown_end = self.cooldown_periods[symbol]
        return datetime.now() < cooldown_end
    
    def _add_cooldown(self, symbol: str, minutes: int = 15):
        """إضافة فترة تهدئة"""
        self.cooldown_periods[symbol] = datetime.now() + timedelta(minutes=minutes)
        self.logger.info(f"تم إضافة فترة تهدئة لـ {symbol} لمدة {minutes} دقيقة")
    
    def add_to_blacklist(self, symbol: str, reason: str = ""):
        """إضافة زوج للقائمة السوداء"""
        self.blacklisted_pairs.add(symbol)
        self.logger.warning(f"تم إضافة {symbol} للقائمة السوداء. السبب: {reason}")
    
    def remove_from_blacklist(self, symbol: str):
        """إزالة زوج من القائمة السوداء"""
        self.blacklisted_pairs.discard(symbol)
        self.logger.info(f"تم إزالة {symbol} من القائمة السوداء")
    
    def get_performance_stats(self) -> Dict:
        """الحصول على إحصائيات الأداء"""
        try:
            if not self.trade_history:
                return {
                    'total_trades': 0,
                    'successful_trades': 0,
                    'success_rate': 0,
                    'total_profit': 0,
                    'average_profit': 0,
                    'daily_stats': {}
                }
            
            total_trades = len(self.trade_history)
            successful_trades = len([t for t in self.trade_history if t['success']])
            success_rate = (successful_trades / total_trades) * 100
            total_profit = sum([t['profit'] for t in self.trade_history])
            average_profit = total_profit / total_trades
            
            # إحصائيات يومية
            daily_stats = {}
            for trade in self.trade_history:
                date = trade['timestamp'].date()
                if date not in daily_stats:
                    daily_stats[date] = {
                        'trades': 0,
                        'profit': 0,
                        'successful': 0
                    }
                
                daily_stats[date]['trades'] += 1
                daily_stats[date]['profit'] += trade['profit']
                if trade['success']:
                    daily_stats[date]['successful'] += 1
            
            return {
                'total_trades': total_trades,
                'successful_trades': successful_trades,
                'success_rate': success_rate,
                'total_profit': total_profit,
                'average_profit': average_profit,
                'daily_stats': {str(k): v for k, v in daily_stats.items()}
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في حساب إحصائيات الأداء: {e}")
            return {}
    
    def emergency_stop(self, reason: str = ""):
        """إيقاف طارئ للتداول"""
        self.logger.critical(f"تم تفعيل الإيقاف الطارئ. السبب: {reason}")
        
        # إضافة جميع الأزواج للقائمة السوداء مؤقتاً
        for symbol in Config.SUPPORTED_PAIRS:
            self.add_to_blacklist(symbol, f"إيقاف طارئ: {reason}")
        
        return True
    
    def reset_daily_limits(self):
        """إعادة تعيين الحدود اليومية"""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # إزالة بيانات الأمس
        if yesterday in self.daily_losses:
            del self.daily_losses[yesterday]
        
        # تنظيف سجل التداول القديم (الاحتفاظ بآخر 30 يوم)
        cutoff_date = datetime.now() - timedelta(days=30)
        self.trade_history = [t for t in self.trade_history 
                            if t['timestamp'] > cutoff_date]
        
        self.logger.info("تم إعادة تعيين الحدود اليومية")

