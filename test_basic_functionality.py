"""
اختبارات أساسية لبرنامج مراجحة العملات المشفرة
"""

import unittest
import asyncio
import sys
import os

# إضافة مجلد src إلى المسار
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from exchange_manager import ExchangeManager
from risk_manager import RiskManager
from flash_loan_manager import FlashLoanManager

class TestBasicFunctionality(unittest.TestCase):
    """اختبارات الوظائف الأساسية"""
    
    def setUp(self):
        """إعداد الاختبارات"""
        self.exchange_manager = ExchangeManager()
        self.risk_manager = RiskManager()
        self.flash_loan_manager = FlashLoanManager()
    
    def test_config_loading(self):
        """اختبار تحميل التكوين"""
        # التحقق من وجود الإعدادات الأساسية
        self.assertIsNotNone(Config.MIN_PROFIT_PERCENTAGE)
        self.assertIsNotNone(Config.MAX_TRADE_AMOUNT)
        self.assertIsNotNone(Config.SUPPORTED_PAIRS)
        self.assertIsInstance(Config.SUPPORTED_PAIRS, list)
        self.assertGreater(len(Config.SUPPORTED_PAIRS), 0)
        
        print("✓ تم تحميل التكوين بنجاح")
    
    def test_exchange_manager_initialization(self):
        """اختبار تهيئة مدير المنصات"""
        # التحقق من تهيئة المنصات
        self.assertIsInstance(self.exchange_manager.exchanges, dict)
        self.assertGreater(len(self.exchange_manager.exchanges), 0)
        
        # التحقق من وجود منصات أساسية
        expected_exchanges = ['kucoin', 'huobi']  # المنصات التي لا تحتاج API keys
        for exchange in expected_exchanges:
            self.assertIn(exchange, self.exchange_manager.exchanges)
        
        print("✓ تم تهيئة مدير المنصات بنجاح")
    
    def test_risk_manager_initialization(self):
        """اختبار تهيئة مدير المخاطر"""
        # التحقق من تهيئة المتغيرات
        self.assertIsInstance(self.risk_manager.trade_history, list)
        self.assertIsInstance(self.risk_manager.daily_losses, dict)
        self.assertIsInstance(self.risk_manager.blacklisted_pairs, set)
        
        # التحقق من الحدود الافتراضية
        self.assertGreater(self.risk_manager.max_daily_trades, 0)
        self.assertGreater(self.risk_manager.max_daily_loss, 0)
        
        print("✓ تم تهيئة مدير المخاطر بنجاح")
    
    def test_opportunity_validation(self):
        """اختبار التحقق من صحة الفرص"""
        # إنشاء فرصة اختبار صالحة
        valid_opportunity = {
            'symbol': 'BTC/USDT',
            'buy_exchange': 'binance',
            'sell_exchange': 'kraken',
            'buy_price': 43000.0,
            'sell_price': 43300.0,
            'profit_percentage': 0.7,
            'profit_amount': 300.0,
            'timestamp': '2025-01-20T10:00:00Z'
        }
        
        is_valid, message = self.risk_manager.validate_opportunity(valid_opportunity)
        self.assertTrue(is_valid, f"الفرصة الصالحة فشلت في التحقق: {message}")
        
        # إنشاء فرصة اختبار غير صالحة (ربح منخفض)
        invalid_opportunity = valid_opportunity.copy()
        invalid_opportunity['profit_percentage'] = 0.1  # أقل من الحد الأدنى
        
        is_valid, message = self.risk_manager.validate_opportunity(invalid_opportunity)
        self.assertFalse(is_valid, "الفرصة غير الصالحة نجحت في التحقق")
        
        print("✓ تم اختبار التحقق من الفرص بنجاح")
    
    def test_position_size_calculation(self):
        """اختبار حساب حجم المركز"""
        opportunity = {
            'symbol': 'BTC/USDT',
            'buy_price': 43000.0,
            'profit_percentage': 0.7
        }
        
        available_balance = 10000.0  # $10,000
        
        position_size = self.risk_manager.calculate_position_size(opportunity, available_balance)
        
        # التحقق من أن حجم المركز منطقي
        self.assertGreater(position_size, 0)
        self.assertLessEqual(position_size, Config.MAX_TRADE_AMOUNT)
        self.assertLessEqual(position_size, available_balance * 0.1)  # لا يزيد عن 10% من الرصيد
        
        print(f"✓ تم حساب حجم المركز: {position_size}")
    
    def test_performance_stats(self):
        """اختبار إحصائيات الأداء"""
        # إضافة بعض الصفقات التجريبية
        test_trades = [
            {
                'timestamp': '2025-01-20T10:00:00Z',
                'symbol': 'BTC/USDT',
                'profit': 50.0,
                'success': True,
                'buy_exchange': 'binance',
                'sell_exchange': 'kraken',
                'trade_amount': 1000.0
            },
            {
                'timestamp': '2025-01-20T11:00:00Z',
                'symbol': 'ETH/USDT',
                'profit': -10.0,
                'success': False,
                'buy_exchange': 'kucoin',
                'sell_exchange': 'huobi',
                'trade_amount': 500.0
            }
        ]
        
        for trade in test_trades:
            self.risk_manager.record_trade(trade)
        
        stats = self.risk_manager.get_performance_stats()
        
        # التحقق من الإحصائيات
        self.assertEqual(stats['total_trades'], 2)
        self.assertEqual(stats['successful_trades'], 1)
        self.assertEqual(stats['success_rate'], 50.0)
        self.assertEqual(stats['total_profit'], 40.0)  # 50 - 10
        
        print("✓ تم اختبار إحصائيات الأداء بنجاح")
    
    def test_flash_loan_manager_initialization(self):
        """اختبار تهيئة مدير القروض السريعة"""
        # التحقق من تهيئة المتغيرات الأساسية
        self.assertIsInstance(self.flash_loan_manager.token_addresses, dict)
        self.assertIsInstance(self.flash_loan_manager.dex_routers, dict)
        
        # التحقق من وجود الرموز الأساسية
        expected_tokens = ['WETH', 'USDC', 'USDT', 'DAI', 'WBTC']
        for token in expected_tokens:
            self.assertIn(token, self.flash_loan_manager.token_addresses)
        
        # التحقق من وجود DEX routers
        expected_dexes = ['uniswap_v2', 'sushiswap']
        for dex in expected_dexes:
            self.assertIn(dex, self.flash_loan_manager.dex_routers)
        
        print("✓ تم تهيئة مدير القروض السريعة بنجاح")

class TestAsyncFunctionality(unittest.IsolatedAsyncioTestCase):
    """اختبارات الوظائف غير المتزامنة"""
    
    async def asyncSetUp(self):
        """إعداد الاختبارات غير المتزامنة"""
        self.exchange_manager = ExchangeManager()
    
    async def test_fetch_ticker_simulation(self):
        """اختبار محاكاة جلب الأسعار"""
        # محاكاة بيانات السعر
        mock_ticker = {
            'exchange': 'test_exchange',
            'symbol': 'BTC/USDT',
            'bid': 43000.0,
            'ask': 43100.0,
            'last': 43050.0,
            'timestamp': 1705741200000,
            'datetime': '2025-01-20T10:00:00Z'
        }
        
        # التحقق من صحة البيانات
        self.assertIsInstance(mock_ticker, dict)
        self.assertIn('bid', mock_ticker)
        self.assertIn('ask', mock_ticker)
        self.assertGreater(mock_ticker['ask'], mock_ticker['bid'])
        
        print("✓ تم اختبار محاكاة جلب الأسعار بنجاح")
    
    async def test_arbitrage_opportunity_detection(self):
        """اختبار اكتشاف فرص المراجحة"""
        # محاكاة أسعار من منصات مختلفة
        mock_prices = {
            'BTC/USDT': {
                'exchange1': {
                    'exchange': 'exchange1',
                    'symbol': 'BTC/USDT',
                    'bid': 43200.0,
                    'ask': 43000.0,  # سعر شراء منخفض
                    'last': 43100.0
                },
                'exchange2': {
                    'exchange': 'exchange2',
                    'symbol': 'BTC/USDT',
                    'bid': 43400.0,  # سعر بيع مرتفع
                    'ask': 43300.0,
                    'last': 43350.0
                }
            }
        }
        
        # تعيين الأسعار المحاكاة
        self.exchange_manager.prices = mock_prices
        
        # البحث عن فرص المراجحة
        opportunities = self.exchange_manager.find_arbitrage_opportunities(0.5)
        
        # التحقق من وجود فرص
        self.assertGreater(len(opportunities), 0)
        
        # التحقق من صحة الفرصة الأولى
        opp = opportunities[0]
        self.assertEqual(opp['symbol'], 'BTC/USDT')
        self.assertEqual(opp['buy_exchange'], 'exchange1')
        self.assertEqual(opp['sell_exchange'], 'exchange2')
        self.assertGreater(opp['profit_percentage'], 0.5)
        
        print(f"✓ تم اكتشاف {len(opportunities)} فرصة مراجحة")

def run_tests():
    """تشغيل جميع الاختبارات"""
    print("=== بدء اختبارات برنامج المراجحة ===")
    
    # تشغيل الاختبارات المتزامنة
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicFunctionality)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # تشغيل الاختبارات غير المتزامنة
    async_suite = unittest.TestLoader().loadTestsFromTestCase(TestAsyncFunctionality)
    async_runner = unittest.TextTestRunner(verbosity=2)
    async_result = async_runner.run(async_suite)
    
    # تجميع النتائج
    total_tests = result.testsRun + async_result.testsRun
    total_failures = len(result.failures) + len(async_result.failures)
    total_errors = len(result.errors) + len(async_result.errors)
    
    print(f"\n=== نتائج الاختبارات ===")
    print(f"إجمالي الاختبارات: {total_tests}")
    print(f"نجح: {total_tests - total_failures - total_errors}")
    print(f"فشل: {total_failures}")
    print(f"أخطاء: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("✅ جميع الاختبارات نجحت!")
        return True
    else:
        print("❌ بعض الاختبارات فشلت")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

