"""
اختبارات محسنة لبرنامج مراجحة العملات المشفرة
"""

import unittest
import asyncio
import sys
import os
from datetime import datetime

# إضافة مجلد src إلى المسار
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from exchange_manager import ExchangeManager
from risk_manager import RiskManager

class TestImprovedFunctionality(unittest.TestCase):
    """اختبارات محسنة للوظائف الأساسية"""
    
    def setUp(self):
        """إعداد الاختبارات"""
        self.exchange_manager = ExchangeManager()
        self.risk_manager = RiskManager()
    
    def test_config_validation(self):
        """اختبار التحقق من صحة التكوين"""
        # التحقق من الإعدادات الأساسية
        self.assertIsInstance(Config.MIN_PROFIT_PERCENTAGE, (int, float))
        self.assertGreater(Config.MIN_PROFIT_PERCENTAGE, 0)
        
        self.assertIsInstance(Config.MAX_TRADE_AMOUNT, (int, float))
        self.assertGreater(Config.MAX_TRADE_AMOUNT, 0)
        
        self.assertIsInstance(Config.SUPPORTED_PAIRS, list)
        self.assertGreater(len(Config.SUPPORTED_PAIRS), 0)
        
        # التحقق من صحة أزواج التداول
        for pair in Config.SUPPORTED_PAIRS:
            self.assertIn('/', pair)
            parts = pair.split('/')
            self.assertEqual(len(parts), 2)
            self.assertTrue(all(len(part) >= 2 for part in parts))
        
        print("✓ تم التحقق من صحة التكوين")
    
    def test_exchange_manager_basic_setup(self):
        """اختبار الإعداد الأساسي لمدير المنصات"""
        # التحقق من تهيئة المتغيرات الأساسية
        self.assertIsInstance(self.exchange_manager.exchanges, dict)
        self.assertIsInstance(self.exchange_manager.prices, dict)
        self.assertIsInstance(self.exchange_manager.last_update, dict)
        
        # التحقق من وجود منصة واحدة على الأقل
        self.assertGreater(len(self.exchange_manager.exchanges), 0)
        
        print(f"✓ تم إعداد {len(self.exchange_manager.exchanges)} منصة")
    
    def test_risk_manager_limits(self):
        """اختبار حدود مدير المخاطر"""
        # التحقق من الحدود الافتراضية
        self.assertGreater(self.risk_manager.max_daily_trades, 0)
        self.assertGreater(self.risk_manager.max_daily_loss, 0)
        
        # التحقق من تهيئة المجموعات
        self.assertIsInstance(self.risk_manager.trade_history, list)
        self.assertIsInstance(self.risk_manager.daily_losses, dict)
        self.assertIsInstance(self.risk_manager.blacklisted_pairs, set)
        
        print("✓ تم التحقق من حدود مدير المخاطر")
    
    def test_opportunity_validation_scenarios(self):
        """اختبار سيناريوهات مختلفة للتحقق من الفرص"""
        
        # سيناريو 1: فرصة صالحة
        valid_opportunity = {
            'symbol': 'BTC/USDT',
            'buy_exchange': 'binance',
            'sell_exchange': 'kraken',
            'buy_price': 43000.0,
            'sell_price': 43300.0,
            'profit_percentage': 0.7,
            'profit_amount': 300.0,
            'timestamp': datetime.now()
        }
        
        is_valid, message = self.risk_manager.validate_opportunity(valid_opportunity)
        self.assertTrue(is_valid, f"الفرصة الصالحة فشلت: {message}")
        
        # سيناريو 2: ربح منخفض
        low_profit_opp = valid_opportunity.copy()
        low_profit_opp['profit_percentage'] = 0.1
        
        is_valid, message = self.risk_manager.validate_opportunity(low_profit_opp)
        self.assertFalse(is_valid)
        self.assertIn("الحد الأدنى", message)
        
        # سيناريو 3: انتشار مشبوه
        suspicious_opp = valid_opportunity.copy()
        suspicious_opp['profit_percentage'] = 15.0  # 15% مشبوه
        
        is_valid, message = self.risk_manager.validate_opportunity(suspicious_opp)
        self.assertFalse(is_valid)
        self.assertIn("مشبوه", message)
        
        print("✓ تم اختبار سيناريوهات التحقق من الفرص")
    
    def test_position_size_calculation_scenarios(self):
        """اختبار سيناريوهات حساب حجم المركز"""
        
        opportunity = {
            'symbol': 'BTC/USDT',
            'buy_price': 43000.0,
            'profit_percentage': 0.7
        }
        
        # سيناريو 1: رصيد كبير
        large_balance = 100000.0
        position_size = self.risk_manager.calculate_position_size(opportunity, large_balance)
        self.assertGreater(position_size, 0)
        self.assertLessEqual(position_size, Config.MAX_TRADE_AMOUNT)
        
        # سيناريو 2: رصيد صغير
        small_balance = 100.0
        position_size = self.risk_manager.calculate_position_size(opportunity, small_balance)
        self.assertGreaterEqual(position_size, 0)  # قد يكون صفر للرصيد الصغير
        
        # سيناريو 3: رصيد متوسط
        medium_balance = 5000.0
        position_size = self.risk_manager.calculate_position_size(opportunity, medium_balance)
        self.assertGreater(position_size, 0)
        self.assertLessEqual(position_size, medium_balance * 0.1)
        
        print("✓ تم اختبار سيناريوهات حساب حجم المركز")
    
    def test_blacklist_functionality(self):
        """اختبار وظائف القائمة السوداء"""
        test_symbol = 'TEST/USDT'
        
        # إضافة للقائمة السوداء
        self.risk_manager.add_to_blacklist(test_symbol, "اختبار")
        self.assertIn(test_symbol, self.risk_manager.blacklisted_pairs)
        
        # اختبار رفض الفرصة المدرجة في القائمة السوداء
        blacklisted_opportunity = {
            'symbol': test_symbol,
            'buy_exchange': 'binance',
            'sell_exchange': 'kraken',
            'buy_price': 1.0,
            'sell_price': 1.01,
            'profit_percentage': 1.0,
            'profit_amount': 0.01,
            'timestamp': datetime.now()
        }
        
        is_valid, message = self.risk_manager.validate_opportunity(blacklisted_opportunity)
        self.assertFalse(is_valid)
        self.assertIn("القائمة السوداء", message)
        
        # إزالة من القائمة السوداء
        self.risk_manager.remove_from_blacklist(test_symbol)
        self.assertNotIn(test_symbol, self.risk_manager.blacklisted_pairs)
        
        print("✓ تم اختبار وظائف القائمة السوداء")
    
    def test_trade_recording_and_stats(self):
        """اختبار تسجيل الصفقات والإحصائيات"""
        # مسح السجل السابق
        self.risk_manager.trade_history = []
        
        # إضافة صفقات تجريبية
        test_trades = [
            {
                'timestamp': datetime.now(),
                'symbol': 'BTC/USDT',
                'profit': 100.0,
                'success': True,
                'buy_exchange': 'binance',
                'sell_exchange': 'kraken',
                'trade_amount': 1000.0
            },
            {
                'timestamp': datetime.now(),
                'symbol': 'ETH/USDT',
                'profit': 50.0,
                'success': True,
                'buy_exchange': 'kucoin',
                'sell_exchange': 'huobi',
                'trade_amount': 500.0
            },
            {
                'timestamp': datetime.now(),
                'symbol': 'ADA/USDT',
                'profit': -20.0,
                'success': False,
                'buy_exchange': 'binance',
                'sell_exchange': 'kraken',
                'trade_amount': 200.0
            }
        ]
        
        for trade in test_trades:
            self.risk_manager.record_trade(trade)
        
        # التحقق من الإحصائيات
        stats = self.risk_manager.get_performance_stats()
        
        self.assertEqual(stats['total_trades'], 3)
        self.assertEqual(stats['successful_trades'], 2)
        self.assertEqual(stats['success_rate'], 66.67)  # تقريباً
        self.assertEqual(stats['total_profit'], 130.0)  # 100 + 50 - 20
        self.assertAlmostEqual(stats['average_profit'], 43.33, places=1)
        
        print("✓ تم اختبار تسجيل الصفقات والإحصائيات")
    
    def test_arbitrage_opportunity_detection_logic(self):
        """اختبار منطق اكتشاف فرص المراجحة"""
        # إعداد أسعار محاكاة
        mock_prices = {
            'BTC/USDT': {
                'exchange_low': {
                    'exchange': 'exchange_low',
                    'symbol': 'BTC/USDT',
                    'bid': 43200.0,
                    'ask': 43000.0,  # سعر شراء منخفض
                    'last': 43100.0
                },
                'exchange_high': {
                    'exchange': 'exchange_high',
                    'symbol': 'BTC/USDT',
                    'bid': 43500.0,  # سعر بيع مرتفع
                    'ask': 43400.0,
                    'last': 43450.0
                }
            },
            'ETH/USDT': {
                'exchange_same': {
                    'exchange': 'exchange_same',
                    'symbol': 'ETH/USDT',
                    'bid': 2650.0,
                    'ask': 2650.0,
                    'last': 2650.0
                }
            }
        }
        
        # تعيين الأسعار المحاكاة
        self.exchange_manager.prices = mock_prices
        
        # البحث عن فرص المراجحة
        opportunities = self.exchange_manager.find_arbitrage_opportunities(0.5)
        
        # التحقق من النتائج
        self.assertGreater(len(opportunities), 0, "يجب العثور على فرصة واحدة على الأقل")
        
        # التحقق من الفرصة الأولى
        opp = opportunities[0]
        self.assertEqual(opp['symbol'], 'BTC/USDT')
        self.assertEqual(opp['buy_exchange'], 'exchange_low')
        self.assertEqual(opp['sell_exchange'], 'exchange_high')
        self.assertGreater(opp['profit_percentage'], 0.5)
        
        # التحقق من عدم وجود فرص للأسعار المتساوية
        eth_opportunities = [o for o in opportunities if o['symbol'] == 'ETH/USDT']
        self.assertEqual(len(eth_opportunities), 0, "لا يجب العثور على فرص للأسعار المتساوية")
        
        print(f"✓ تم اكتشاف {len(opportunities)} فرصة مراجحة صحيحة")

def run_improved_tests():
    """تشغيل الاختبارات المحسنة"""
    print("=== بدء الاختبارات المحسنة ===")
    
    # إنشاء مجموعة الاختبارات
    suite = unittest.TestLoader().loadTestsFromTestCase(TestImprovedFunctionality)
    
    # تشغيل الاختبارات
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # تحليل النتائج
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    successes = total_tests - failures - errors
    
    print(f"\n=== نتائج الاختبارات المحسنة ===")
    print(f"إجمالي الاختبارات: {total_tests}")
    print(f"نجح: {successes}")
    print(f"فشل: {failures}")
    print(f"أخطاء: {errors}")
    print(f"معدل النجاح: {(successes/total_tests)*100:.1f}%")
    
    if failures == 0 and errors == 0:
        print("✅ جميع الاختبارات المحسنة نجحت!")
        return True
    else:
        print("❌ بعض الاختبارات فشلت")
        
        # طباعة تفاصيل الفشل
        if result.failures:
            print("\n--- تفاصيل الفشل ---")
            for test, traceback in result.failures:
                print(f"فشل: {test}")
                print(traceback)
        
        if result.errors:
            print("\n--- تفاصيل الأخطاء ---")
            for test, traceback in result.errors:
                print(f"خطأ: {test}")
                print(traceback)
        
        return False

if __name__ == '__main__':
    success = run_improved_tests()
    sys.exit(0 if success else 1)

