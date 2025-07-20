"""
مدير المنصات لجلب الأسعار وتنفيذ الصفقات
"""

import ccxt
import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import time
from config import Config

class ExchangeManager:
    """مدير المنصات للتداول والمراجحة"""
    
    def __init__(self):
        self.exchanges = {}
        self.prices = {}
        self.last_update = {}
        self.logger = logging.getLogger(__name__)
        self._initialize_exchanges()
    
    def _initialize_exchanges(self):
        """تهيئة المنصات المدعومة"""
        try:
            # Binance
            if Config.BINANCE_API_KEY and Config.BINANCE_SECRET_KEY:
                self.exchanges['binance'] = ccxt.binance({
                    'apiKey': Config.BINANCE_API_KEY,
                    'secret': Config.BINANCE_SECRET_KEY,
                    'sandbox': False,
                    'enableRateLimit': True,
                    'rateLimit': 1200
                })
                self.logger.info("تم تهيئة منصة Binance بنجاح")
            
            # Coinbase Pro (تم تغيير الاسم إلى coinbase)
            if Config.COINBASE_API_KEY and Config.COINBASE_SECRET_KEY:
                self.exchanges['coinbase'] = ccxt.coinbase({
                    'apiKey': Config.COINBASE_API_KEY,
                    'secret': Config.COINBASE_SECRET_KEY,
                    'sandbox': False,
                    'enableRateLimit': True,
                    'rateLimit': 10000
                })
                self.logger.info("تم تهيئة منصة Coinbase بنجاح")
            
            # Kraken
            if Config.KRAKEN_API_KEY and Config.KRAKEN_SECRET_KEY:
                self.exchanges['kraken'] = ccxt.kraken({
                    'apiKey': Config.KRAKEN_API_KEY,
                    'secret': Config.KRAKEN_SECRET_KEY,
                    'sandbox': False,
                    'enableRateLimit': True,
                    'rateLimit': 3000
                })
                self.logger.info("تم تهيئة منصة Kraken بنجاح")
            
            # إضافة منصات أخرى بدون API keys للمراقبة فقط
            self.exchanges['kucoin'] = ccxt.kucoin({
                'enableRateLimit': True,
                'rateLimit': 1000
            })
            
            self.exchanges['huobi'] = ccxt.huobi({
                'enableRateLimit': True,
                'rateLimit': 2000
            })
            
            self.logger.info(f"تم تهيئة {len(self.exchanges)} منصة")
            
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة المنصات: {e}")
    
    async def fetch_ticker(self, exchange_name: str, symbol: str) -> Optional[Dict]:
        """جلب سعر زوج تداول من منصة معينة"""
        try:
            if exchange_name not in self.exchanges:
                return None
            
            exchange = self.exchanges[exchange_name]
            ticker = await exchange.fetch_ticker(symbol)
            
            return {
                'exchange': exchange_name,
                'symbol': symbol,
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'timestamp': ticker['timestamp'],
                'datetime': ticker['datetime']
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب السعر من {exchange_name} لـ {symbol}: {e}")
            return None
    
    async def fetch_all_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Dict]]:
        """جلب الأسعار من جميع المنصات لجميع الأزواج"""
        all_prices = {}
        
        tasks = []
        for exchange_name in self.exchanges.keys():
            for symbol in symbols:
                task = self.fetch_ticker(exchange_name, symbol)
                tasks.append((exchange_name, symbol, task))
        
        results = await asyncio.gather(*[task for _, _, task in tasks], return_exceptions=True)
        
        for i, result in enumerate(results):
            exchange_name, symbol, _ = tasks[i]
            
            if isinstance(result, Exception):
                continue
            
            if result is None:
                continue
            
            if symbol not in all_prices:
                all_prices[symbol] = {}
            
            all_prices[symbol][exchange_name] = result
        
        self.prices = all_prices
        self.last_update = datetime.now()
        
        return all_prices
    
    def find_arbitrage_opportunities(self, min_profit_percentage: float = 0.5) -> List[Dict]:
        """البحث عن فرص المراجحة"""
        opportunities = []
        
        for symbol, exchange_prices in self.prices.items():
            if len(exchange_prices) < 2:
                continue
            
            # العثور على أقل سعر شراء وأعلى سعر بيع
            min_ask = float('inf')
            max_bid = 0
            min_exchange = None
            max_exchange = None
            
            for exchange_name, price_data in exchange_prices.items():
                if price_data and price_data.get('ask') and price_data.get('bid'):
                    ask = price_data['ask']
                    bid = price_data['bid']
                    
                    if ask < min_ask:
                        min_ask = ask
                        min_exchange = exchange_name
                    
                    if bid > max_bid:
                        max_bid = bid
                        max_exchange = exchange_name
            
            # حساب الربح المحتمل
            if min_ask < float('inf') and max_bid > 0 and min_exchange != max_exchange:
                profit_percentage = ((max_bid - min_ask) / min_ask) * 100
                
                if profit_percentage >= min_profit_percentage:
                    opportunity = {
                        'symbol': symbol,
                        'buy_exchange': min_exchange,
                        'sell_exchange': max_exchange,
                        'buy_price': min_ask,
                        'sell_price': max_bid,
                        'profit_percentage': profit_percentage,
                        'profit_amount': max_bid - min_ask,
                        'timestamp': datetime.now()
                    }
                    opportunities.append(opportunity)
        
        # ترتيب الفرص حسب نسبة الربح
        opportunities.sort(key=lambda x: x['profit_percentage'], reverse=True)
        
        return opportunities
    
    async def get_order_book(self, exchange_name: str, symbol: str, limit: int = 20) -> Optional[Dict]:
        """جلب دفتر الأوامر"""
        try:
            if exchange_name not in self.exchanges:
                return None
            
            exchange = self.exchanges[exchange_name]
            order_book = await exchange.fetch_order_book(symbol, limit)
            
            return {
                'exchange': exchange_name,
                'symbol': symbol,
                'bids': order_book['bids'],
                'asks': order_book['asks'],
                'timestamp': order_book['timestamp']
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب دفتر الأوامر من {exchange_name}: {e}")
            return None
    
    async def calculate_optimal_trade_size(self, opportunity: Dict, max_amount: float) -> float:
        """حساب حجم التداول الأمثل"""
        try:
            buy_exchange = opportunity['buy_exchange']
            sell_exchange = opportunity['sell_exchange']
            symbol = opportunity['symbol']
            
            # جلب دفاتر الأوامر
            buy_book = await self.get_order_book(buy_exchange, symbol)
            sell_book = await self.get_order_book(sell_exchange, symbol)
            
            if not buy_book or not sell_book:
                return min(max_amount, Config.MIN_TRADE_AMOUNT)
            
            # حساب السيولة المتاحة
            buy_liquidity = sum([bid[1] for bid in buy_book['asks'][:5]])  # أول 5 مستويات
            sell_liquidity = sum([ask[1] for ask in sell_book['bids'][:5]])
            
            # الحد الأقصى للتداول بناءً على السيولة
            max_by_liquidity = min(buy_liquidity, sell_liquidity) * 0.8  # 80% من السيولة
            
            return min(max_amount, max_by_liquidity, Config.MAX_TRADE_AMOUNT)
            
        except Exception as e:
            self.logger.error(f"خطأ في حساب حجم التداول: {e}")
            return Config.MIN_TRADE_AMOUNT
    
    async def execute_arbitrage_trade(self, opportunity: Dict, trade_amount: float) -> Dict:
        """تنفيذ صفقة المراجحة"""
        try:
            buy_exchange_name = opportunity['buy_exchange']
            sell_exchange_name = opportunity['sell_exchange']
            symbol = opportunity['symbol']
            
            buy_exchange = self.exchanges.get(buy_exchange_name)
            sell_exchange = self.exchanges.get(sell_exchange_name)
            
            if not buy_exchange or not sell_exchange:
                return {'success': False, 'error': 'منصة غير متاحة'}
            
            # التحقق من الأرصدة
            buy_balance = await self._check_balance(buy_exchange, symbol.split('/')[1])  # USDT
            sell_balance = await self._check_balance(sell_exchange, symbol.split('/')[0])  # BTC
            
            if buy_balance < trade_amount:
                return {'success': False, 'error': 'رصيد غير كافي للشراء'}
            
            # تنفيذ الصفقات
            buy_order = await buy_exchange.create_market_buy_order(symbol, trade_amount)
            
            if buy_order['status'] == 'closed':
                # بيع في المنصة الأخرى
                sell_order = await sell_exchange.create_market_sell_order(
                    symbol, 
                    buy_order['filled']
                )
                
                return {
                    'success': True,
                    'buy_order': buy_order,
                    'sell_order': sell_order,
                    'profit': (sell_order['cost'] - buy_order['cost']),
                    'timestamp': datetime.now()
                }
            else:
                return {'success': False, 'error': 'فشل في تنفيذ أمر الشراء'}
                
        except Exception as e:
            self.logger.error(f"خطأ في تنفيذ المراجحة: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _check_balance(self, exchange, currency: str) -> float:
        """التحقق من الرصيد"""
        try:
            balance = await exchange.fetch_balance()
            return balance.get(currency, {}).get('free', 0)
        except Exception as e:
            self.logger.error(f"خطأ في جلب الرصيد: {e}")
            return 0
    
    def get_supported_symbols(self, exchange_name: str) -> List[str]:
        """الحصول على الأزواج المدعومة في منصة معينة"""
        try:
            if exchange_name not in self.exchanges:
                return []
            
            exchange = self.exchanges[exchange_name]
            markets = exchange.load_markets()
            
            # فلترة الأزواج المدعومة
            supported = []
            for symbol in Config.SUPPORTED_PAIRS:
                if symbol in markets:
                    supported.append(symbol)
            
            return supported
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب الأزواج المدعومة: {e}")
            return []
    
    def close_all_connections(self):
        """إغلاق جميع الاتصالات"""
        for exchange in self.exchanges.values():
            try:
                if hasattr(exchange, 'close'):
                    exchange.close()
            except Exception as e:
                self.logger.error(f"خطأ في إغلاق الاتصال: {e}")
        
        self.logger.info("تم إغلاق جميع اتصالات المنصات")

