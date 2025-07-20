"""
اختبار أداء شامل لنظام مراجحة العملات المشفرة
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta

# إضافة مجلد src إلى المسار
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from exchange_manager import ExchangeManager
from risk_manager import RiskManager
from flash_loan_manager import FlashLoanManager

class SystemPerformanceTest:
    """اختبار أداء النظام الشامل"""
    
    def __init__(self):
        self.results = {
            'test_start_time': datetime.now().isoformat(),
            'config_test': {},
            'exchange_manager_test': {},
            'risk_manager_test': {},
            'flash_loan_manager_test': {},
            'integration_test': {},
            'performance_metrics': {},
            'recommendations': []
        }
    
    def run_comprehensive_test(self):
        """تشغيل اختبار شامل للنظام"""
        print("=== بدء اختبار الأداء الشامل ===")
        
        # اختبار التكوين
        self.test_configuration()
        
        # اختبار مدير المنصات
        self.test_exchange_manager()
        
        # اختبار مدير المخاطر
        self.test_risk_manager()
        
        # اختبار مدير القروض السريعة
        self.test_flash_loan_manager()
        
        # اختبار التكامل
        self.test_integration()
        
        # تحليل الأداء
        self.analyze_performance()
        
        # إنتاج التقرير
        self.generate_report()
        
        return self.results
    
    def test_configuration(self):
        """اختبار التكوين"""
        print("اختبار التكوين...")
        start_time = time.time()
        
        try:
            # التحقق من الإعدادات الأساسية
            config_issues = []
            
            if Config.MIN_PROFIT_PERCENTAGE <= 0:
                config_issues.append("MIN_PROFIT_PERCENTAGE يجب أن يكون أكبر من صفر")
            
            if Config.MAX_TRADE_AMOUNT <= Config.MIN_TRADE_AMOUNT:
                config_issues.append("MAX_TRADE_AMOUNT يجب أن يكون أكبر من MIN_TRADE_AMOUNT")
            
            if not Config.SUPPORTED_PAIRS:
                config_issues.append("SUPPORTED_PAIRS فارغة")
            
            # التحقق من صحة أزواج التداول
            invalid_pairs = []
            for pair in Config.SUPPORTED_PAIRS:
                if '/' not in pair or len(pair.split('/')) != 2:
                    invalid_pairs.append(pair)
            
            if invalid_pairs:
                config_issues.append(f"أزواج تداول غير صحيحة: {invalid_pairs}")
            
            self.results['config_test'] = {
                'status': 'success' if not config_issues else 'warning',
                'issues': config_issues,
                'supported_pairs_count': len(Config.SUPPORTED_PAIRS),
                'test_duration': time.time() - start_time
            }
            
            print(f"✓ اختبار التكوين مكتمل ({len(config_issues)} مشاكل)")
            
        except Exception as e:
            self.results['config_test'] = {
                'status': 'error',
                'error': str(e),
                'test_duration': time.time() - start_time
            }
            print(f"✗ خطأ في اختبار التكوين: {e}")
    
    def test_exchange_manager(self):
        """اختبار مدير المنصات"""
        print("اختبار مدير المنصات...")
        start_time = time.time()
        
        try:
            exchange_manager = ExchangeManager()
            
            # التحقق من تهيئة المنصات
            initialized_exchanges = len(exchange_manager.exchanges)
            
            # اختبار اكتشاف الفرص مع بيانات محاكاة
            mock_prices = {
                'BTC/USDT': {
                    'exchange1': {
                        'exchange': 'exchange1',
                        'symbol': 'BTC/USDT',
                        'bid': 43200.0,
                        'ask': 43000.0,
                        'last': 43100.0
                    },
                    'exchange2': {
                        'exchange': 'exchange2',
                        'symbol': 'BTC/USDT',
                        'bid': 43500.0,
                        'ask': 43400.0,
                        'last': 43450.0
                    }
                }
            }
            
            exchange_manager.prices = mock_prices
            opportunities = exchange_manager.find_arbitrage_opportunities(0.5)
            
            self.results['exchange_manager_test'] = {
                'status': 'success',
                'initialized_exchanges': initialized_exchanges,
                'mock_opportunities_found': len(opportunities),
                'test_duration': time.time() - start_time
            }
            
            print(f"✓ مدير المنصات: {initialized_exchanges} منصة، {len(opportunities)} فرصة محاكاة")
            
        except Exception as e:
            self.results['exchange_manager_test'] = {
                'status': 'error',
                'error': str(e),
                'test_duration': time.time() - start_time
            }
            print(f"✗ خطأ في اختبار مدير المنصات: {e}")
    
    def test_risk_manager(self):
        """اختبار مدير المخاطر"""
        print("اختبار مدير المخاطر...")
        start_time = time.time()
        
        try:
            risk_manager = RiskManager()
            
            # اختبار التحقق من الفرص
            test_opportunity = {
                'symbol': 'BTC/USDT',
                'buy_exchange': 'binance',
                'sell_exchange': 'kraken',
                'buy_price': 43000.0,
                'sell_price': 43300.0,
                'profit_percentage': 0.7,
                'profit_amount': 300.0,
                'timestamp': datetime.now()
            }
            
            is_valid, message = risk_manager.validate_opportunity(test_opportunity)
            
            # اختبار حساب حجم المركز
            position_sizes = []
            for balance in [1000, 5000, 10000, 50000]:
                size = risk_manager.calculate_position_size(test_opportunity, balance)
                position_sizes.append({'balance': balance, 'position_size': size})
            
            # اختبار تسجيل الصفقات
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
                    'profit': -20.0,
                    'success': False,
                    'buy_exchange': 'kucoin',
                    'sell_exchange': 'huobi',
                    'trade_amount': 500.0
                }
            ]
            
            for trade in test_trades:
                risk_manager.record_trade(trade)
            
            stats = risk_manager.get_performance_stats()
            
            self.results['risk_manager_test'] = {
                'status': 'success',
                'opportunity_validation': is_valid,
                'position_sizes': position_sizes,
                'performance_stats': stats,
                'test_duration': time.time() - start_time
            }
            
            print(f"✓ مدير المخاطر: التحقق {'نجح' if is_valid else 'فشل'}, {stats['total_trades']} صفقة تجريبية")
            
        except Exception as e:
            self.results['risk_manager_test'] = {
                'status': 'error',
                'error': str(e),
                'test_duration': time.time() - start_time
            }
            print(f"✗ خطأ في اختبار مدير المخاطر: {e}")
    
    def test_flash_loan_manager(self):
        """اختبار مدير القروض السريعة"""
        print("اختبار مدير القروض السريعة...")
        start_time = time.time()
        
        try:
            flash_loan_manager = FlashLoanManager()
            
            # التحقق من تهيئة العناوين
            token_count = len(flash_loan_manager.token_addresses)
            dex_count = len(flash_loan_manager.dex_routers)
            
            # التحقق من معلومات الشبكة
            network_info = flash_loan_manager.get_network_info()
            
            # اختبار تقدير تكلفة الغاز
            gas_estimate = flash_loan_manager.estimate_gas_cost('WETH', 1000)
            
            self.results['flash_loan_manager_test'] = {
                'status': 'success',
                'token_addresses_count': token_count,
                'dex_routers_count': dex_count,
                'network_connected': network_info.get('connected', False),
                'gas_estimate': gas_estimate,
                'test_duration': time.time() - start_time
            }
            
            print(f"✓ مدير القروض السريعة: {token_count} رمز، {dex_count} DEX، "
                  f"شبكة {'متصلة' if network_info.get('connected') else 'غير متصلة'}")
            
        except Exception as e:
            self.results['flash_loan_manager_test'] = {
                'status': 'error',
                'error': str(e),
                'test_duration': time.time() - start_time
            }
            print(f"✗ خطأ في اختبار مدير القروض السريعة: {e}")
    
    def test_integration(self):
        """اختبار التكامل بين المكونات"""
        print("اختبار التكامل...")
        start_time = time.time()
        
        try:
            # إنشاء جميع المكونات
            exchange_manager = ExchangeManager()
            risk_manager = RiskManager()
            flash_loan_manager = FlashLoanManager()
            
            # محاكاة سيناريو مراجحة كامل
            mock_prices = {
                'BTC/USDT': {
                    'binance': {
                        'exchange': 'binance',
                        'symbol': 'BTC/USDT',
                        'bid': 43200.0,
                        'ask': 43000.0,
                        'last': 43100.0
                    },
                    'kraken': {
                        'exchange': 'kraken',
                        'symbol': 'BTC/USDT',
                        'bid': 43500.0,
                        'ask': 43400.0,
                        'last': 43450.0
                    }
                }
            }
            
            # تعيين الأسعار المحاكاة
            exchange_manager.prices = mock_prices
            
            # اكتشاف الفرص
            opportunities = exchange_manager.find_arbitrage_opportunities(0.5)
            
            # التحقق من الفرص
            validated_opportunities = []
            for opp in opportunities:
                is_valid, message = risk_manager.validate_opportunity(opp)
                if is_valid:
                    validated_opportunities.append(opp)
            
            # حساب أحجام المراكز
            position_calculations = []
            for opp in validated_opportunities:
                position_size = risk_manager.calculate_position_size(opp, 10000)
                position_calculations.append({
                    'symbol': opp['symbol'],
                    'position_size': position_size
                })
            
            self.results['integration_test'] = {
                'status': 'success',
                'opportunities_found': len(opportunities),
                'validated_opportunities': len(validated_opportunities),
                'position_calculations': position_calculations,
                'test_duration': time.time() - start_time
            }
            
            print(f"✓ اختبار التكامل: {len(opportunities)} فرصة، {len(validated_opportunities)} صالحة")
            
        except Exception as e:
            self.results['integration_test'] = {
                'status': 'error',
                'error': str(e),
                'test_duration': time.time() - start_time
            }
            print(f"✗ خطأ في اختبار التكامل: {e}")
    
    def analyze_performance(self):
        """تحليل الأداء"""
        print("تحليل الأداء...")
        
        # حساب إجمالي وقت الاختبار
        total_test_time = sum([
            self.results['config_test'].get('test_duration', 0),
            self.results['exchange_manager_test'].get('test_duration', 0),
            self.results['risk_manager_test'].get('test_duration', 0),
            self.results['flash_loan_manager_test'].get('test_duration', 0),
            self.results['integration_test'].get('test_duration', 0)
        ])
        
        # حساب معدل النجاح
        successful_tests = sum([
            1 if self.results['config_test'].get('status') == 'success' else 0,
            1 if self.results['exchange_manager_test'].get('status') == 'success' else 0,
            1 if self.results['risk_manager_test'].get('status') == 'success' else 0,
            1 if self.results['flash_loan_manager_test'].get('status') == 'success' else 0,
            1 if self.results['integration_test'].get('status') == 'success' else 0
        ])
        
        success_rate = (successful_tests / 5) * 100
        
        self.results['performance_metrics'] = {
            'total_test_time': total_test_time,
            'success_rate': success_rate,
            'successful_tests': successful_tests,
            'total_tests': 5
        }
        
        print(f"✓ تحليل الأداء: {success_rate:.1f}% نجاح، {total_test_time:.2f}s إجمالي")
    
    def generate_report(self):
        """إنتاج التقرير النهائي"""
        print("إنتاج التقرير...")
        
        # توصيات بناءً على النتائج
        recommendations = []
        
        # توصيات التكوين
        if self.results['config_test'].get('issues'):
            recommendations.append("إصلاح مشاكل التكوين المذكورة")
        
        # توصيات المنصات
        exchange_count = self.results['exchange_manager_test'].get('initialized_exchanges', 0)
        if exchange_count < 3:
            recommendations.append("إضافة المزيد من مفاتيح API للمنصات لزيادة الفرص")
        
        # توصيات الشبكة
        if not self.results['flash_loan_manager_test'].get('network_connected', False):
            recommendations.append("تكوين اتصال Ethereum للقروض السريعة")
        
        # توصيات الأداء
        if self.results['performance_metrics']['success_rate'] < 80:
            recommendations.append("مراجعة الأخطاء وتحسين استقرار النظام")
        
        self.results['recommendations'] = recommendations
        self.results['test_end_time'] = datetime.now().isoformat()
        
        print(f"✓ التقرير جاهز مع {len(recommendations)} توصية")

def run_system_test():
    """تشغيل اختبار النظام الشامل"""
    test = SystemPerformanceTest()
    results = test.run_comprehensive_test()
    
    # حفظ النتائج
    report_path = '../logs/system_performance_report.json'
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    # طباعة ملخص النهائي
    print("\n" + "="*50)
    print("ملخص اختبار الأداء الشامل")
    print("="*50)
    print(f"معدل النجاح: {results['performance_metrics']['success_rate']:.1f}%")
    print(f"وقت الاختبار: {results['performance_metrics']['total_test_time']:.2f} ثانية")
    print(f"المنصات المهيأة: {results['exchange_manager_test'].get('initialized_exchanges', 0)}")
    print(f"الشبكة متصلة: {'نعم' if results['flash_loan_manager_test'].get('network_connected') else 'لا'}")
    
    if results['recommendations']:
        print("\nالتوصيات:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec}")
    
    print(f"\nتم حفظ التقرير الكامل في: {report_path}")
    
    return results

if __name__ == '__main__':
    run_system_test()

