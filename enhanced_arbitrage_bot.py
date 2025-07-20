"""
برنامج مراجحة العملات المشفرة المحسن مع القروض السريعة
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
import json
from typing import Dict, List
import time

from config import Config
from exchange_manager import ExchangeManager
from risk_manager import RiskManager
from flash_loan_manager import FlashLoanManager

class EnhancedArbitrageBot:
    """البرنامج المحسن للمراجحة مع القروض السريعة"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # التحقق من التكوين
        if not Config.validate_config():
            self.logger.error("تكوين غير صحيح. يرجى التحقق من ملف .env")
            sys.exit(1)
        
        # تهيئة المكونات
        self.exchange_manager = ExchangeManager()
        self.risk_manager = RiskManager()
        self.flash_loan_manager = FlashLoanManager()
        
        # متغيرات التحكم
        self.running = False
        self.flash_loan_enabled = False
        self.stats = {
            'start_time': None,
            'total_opportunities': 0,
            'executed_trades': 0,
            'flash_loan_trades': 0,
            'total_profit': 0,
            'flash_loan_profit': 0,
            'last_update': None
        }
        
        # إعداد معالج الإشارات للإغلاق الآمن
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.logger.info("تم تهيئة برنامج المراجحة المحسن بنجاح")
    
    def setup_logging(self):
        """إعداد نظام التسجيل"""
        import os
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOG_FILE, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def signal_handler(self, signum, frame):
        """معالج إشارات الإغلاق"""
        self.logger.info(f"تم استلام إشارة الإغلاق: {signum}")
        self.stop()
    
    async def start(self, enable_flash_loans: bool = False):
        """بدء تشغيل البرنامج"""
        self.logger.info("بدء تشغيل برنامج المراجحة المحسن...")
        self.running = True
        self.flash_loan_enabled = enable_flash_loans
        self.stats['start_time'] = datetime.now()
        
        if enable_flash_loans:
            # التحقق من إعداد القروض السريعة
            network_info = self.flash_loan_manager.get_network_info()
            if network_info.get('connected'):
                self.logger.info("تم تفعيل وضع القروض السريعة")
                self.logger.info(f"معلومات الشبكة: {network_info}")
            else:
                self.logger.warning("فشل في الاتصال بشبكة Ethereum. سيتم تعطيل القروض السريعة")
                self.flash_loan_enabled = False
        
        try:
            # حلقة التشغيل الرئيسية
            while self.running:
                await self.run_enhanced_arbitrage_cycle()
                await asyncio.sleep(Config.MONITORING_INTERVAL)
                
        except Exception as e:
            self.logger.error(f"خطأ في التشغيل الرئيسي: {e}")
        finally:
            await self.cleanup()
    
    async def run_enhanced_arbitrage_cycle(self):
        """تشغيل دورة مراجحة محسنة"""
        try:
            # جلب الأسعار من جميع المنصات
            self.logger.debug("جلب الأسعار من المنصات...")
            prices = await self.exchange_manager.fetch_all_prices(Config.SUPPORTED_PAIRS)
            
            if not prices:
                self.logger.warning("لم يتم جلب أي أسعار")
                return
            
            # البحث عن فرص المراجحة
            opportunities = self.exchange_manager.find_arbitrage_opportunities(
                Config.MIN_PROFIT_PERCENTAGE
            )
            
            self.stats['total_opportunities'] += len(opportunities)
            
            if opportunities:
                self.logger.info(f"تم العثور على {len(opportunities)} فرصة مراجحة")
                
                # تصنيف الفرص حسب الربحية
                regular_opportunities = []
                flash_loan_opportunities = []
                
                for opp in opportunities[:5]:  # أفضل 5 فرص
                    if self.flash_loan_enabled and opp['profit_percentage'] > 1.0:
                        # فرص عالية الربحية للقروض السريعة
                        flash_loan_opportunities.append(opp)
                    else:
                        # فرص عادية
                        regular_opportunities.append(opp)
                
                # معالجة الفرص العادية
                for opportunity in regular_opportunities:
                    await self.process_regular_opportunity(opportunity)
                
                # معالجة فرص القروض السريعة
                for opportunity in flash_loan_opportunities:
                    await self.process_flash_loan_opportunity(opportunity)
            
            # تحديث الإحصائيات
            self.stats['last_update'] = datetime.now()
            
            # طباعة الإحصائيات كل 10 دورات
            if self.stats['total_opportunities'] % 10 == 0:
                self.print_enhanced_stats()
                
        except Exception as e:
            self.logger.error(f"خطأ في دورة المراجحة المحسنة: {e}")
    
    async def process_regular_opportunity(self, opportunity: Dict):
        """معالجة فرصة مراجحة عادية"""
        try:
            self.logger.info(f"معالجة فرصة عادية: {opportunity['symbol']} - "
                           f"ربح: {opportunity['profit_percentage']:.2f}%")
            
            # التحقق من صحة الفرصة
            is_valid, validation_message = self.risk_manager.validate_opportunity(opportunity)
            
            if not is_valid:
                self.logger.warning(f"فرصة غير صالحة: {validation_message}")
                return
            
            # حساب حجم التداول الأمثل
            trade_amount = await self.exchange_manager.calculate_optimal_trade_size(
                opportunity, Config.MAX_TRADE_AMOUNT
            )
            
            if trade_amount < Config.MIN_TRADE_AMOUNT:
                self.logger.warning(f"حجم التداول صغير جداً: {trade_amount}")
                return
            
            # التحقق من صحة التنفيذ
            can_execute, execution_message = self.risk_manager.validate_trade_execution(
                opportunity, trade_amount
            )
            
            if not can_execute:
                self.logger.warning(f"لا يمكن تنفيذ الصفقة: {execution_message}")
                return
            
            # تنفيذ الصفقة العادية
            trade_result = await self.exchange_manager.execute_arbitrage_trade(
                opportunity, trade_amount
            )
            
            # تسجيل النتيجة
            trade_result.update({
                'symbol': opportunity['symbol'],
                'buy_exchange': opportunity['buy_exchange'],
                'sell_exchange': opportunity['sell_exchange'],
                'trade_amount': trade_amount,
                'trade_type': 'regular'
            })
            
            self.risk_manager.record_trade(trade_result)
            
            if trade_result['success']:
                self.stats['executed_trades'] += 1
                self.stats['total_profit'] += trade_result.get('profit', 0)
                self.logger.info(f"تم تنفيذ الصفقة العادية بنجاح. الربح: {trade_result.get('profit', 0):.4f}")
            else:
                self.logger.error(f"فشل في تنفيذ الصفقة العادية: {trade_result.get('error', 'خطأ غير معروف')}")
            
        except Exception as e:
            self.logger.error(f"خطأ في معالجة الفرصة العادية: {e}")
    
    async def process_flash_loan_opportunity(self, opportunity: Dict):
        """معالجة فرصة مراجحة بالقرض السريع"""
        try:
            if not self.flash_loan_enabled:
                return
            
            self.logger.info(f"معالجة فرصة قرض سريع: {opportunity['symbol']} - "
                           f"ربح: {opportunity['profit_percentage']:.2f}%")
            
            # التحقق من صحة الفرصة للقرض السريع
            is_valid, validation_message = self.risk_manager.validate_opportunity(opportunity)
            
            if not is_valid:
                self.logger.warning(f"فرصة قرض سريع غير صالحة: {validation_message}")
                return
            
            # حساب مبلغ القرض السريع (أكبر من التداول العادي)
            flash_loan_amount = min(
                Config.MAX_TRADE_AMOUNT * 10,  # 10 أضعاف الحد الأقصى العادي
                100000  # حد أقصى للقرض السريع
            )
            
            # تقدير تكلفة الغاز
            gas_estimate = self.flash_loan_manager.estimate_gas_cost(
                opportunity['symbol'].split('/')[0], 
                flash_loan_amount
            )
            
            if not gas_estimate['success']:
                self.logger.error(f"فشل في تقدير تكلفة الغاز: {gas_estimate.get('error')}")
                return
            
            # التحقق من أن الربح المتوقع يغطي تكلفة الغاز
            expected_profit_usd = (opportunity['profit_percentage'] / 100) * flash_loan_amount
            gas_cost_usd = gas_estimate['total_cost_eth'] * 3000  # تقدير سعر ETH
            
            if expected_profit_usd < gas_cost_usd * 2:  # الربح يجب أن يكون ضعف تكلفة الغاز
                self.logger.warning(f"الربح المتوقع لا يغطي تكلفة الغاز. "
                                  f"ربح: ${expected_profit_usd:.2f}, غاز: ${gas_cost_usd:.2f}")
                return
            
            # تحديد الرموز والمنصات
            token_pair = opportunity['symbol'].split('/')
            token_a = token_pair[0]
            token_b = token_pair[1]
            
            # تحويل أسماء المنصات إلى عناوين DEX
            buy_dex = self._get_dex_name(opportunity['buy_exchange'])
            sell_dex = self._get_dex_name(opportunity['sell_exchange'])
            
            if not buy_dex or not sell_dex:
                self.logger.warning("منصة غير مدعومة للقروض السريعة")
                return
            
            # تنفيذ القرض السريع
            self.logger.info(f"تنفيذ قرض سريع: {flash_loan_amount} {token_a}")
            
            flash_result = await self.flash_loan_manager.execute_flash_loan_arbitrage(
                token_a=token_a,
                token_b=token_b,
                amount=int(flash_loan_amount * 10**18),  # تحويل إلى wei
                buy_dex=buy_dex,
                sell_dex=sell_dex,
                min_profit=int(expected_profit_usd * 0.5 * 10**18)  # 50% من الربح المتوقع كحد أدنى
            )
            
            # تسجيل النتيجة
            trade_result = {
                'success': flash_result['success'],
                'symbol': opportunity['symbol'],
                'buy_exchange': opportunity['buy_exchange'],
                'sell_exchange': opportunity['sell_exchange'],
                'trade_amount': flash_loan_amount,
                'trade_type': 'flash_loan',
                'tx_hash': flash_result.get('tx_hash'),
                'gas_used': flash_result.get('gas_used'),
                'error': flash_result.get('error')
            }
            
            if flash_result['success']:
                # حساب الربح الفعلي من الأحداث
                events = flash_result.get('events', [])
                actual_profit = 0
                
                for event in events:
                    if event['type'] == 'ArbitrageExecuted':
                        actual_profit = event['profit'] / 10**18  # تحويل من wei
                        break
                
                trade_result['profit'] = actual_profit
                
                self.stats['flash_loan_trades'] += 1
                self.stats['flash_loan_profit'] += actual_profit
                self.stats['total_profit'] += actual_profit
                
                self.logger.info(f"تم تنفيذ القرض السريع بنجاح. "
                               f"الربح: {actual_profit:.4f} {token_a}, "
                               f"TX: {flash_result['tx_hash']}")
            else:
                self.logger.error(f"فشل في تنفيذ القرض السريع: {flash_result.get('error')}")
            
            self.risk_manager.record_trade(trade_result)
            
        except Exception as e:
            self.logger.error(f"خطأ في معالجة فرصة القرض السريع: {e}")
    
    def _get_dex_name(self, exchange_name: str) -> str:
        """تحويل اسم المنصة إلى اسم DEX"""
        dex_mapping = {
            'uniswap': 'uniswap_v2',
            'sushiswap': 'sushiswap',
            'pancakeswap': 'pancakeswap'
        }
        
        for dex_key, dex_name in dex_mapping.items():
            if dex_key in exchange_name.lower():
                return dex_name
        
        return None
    
    def print_enhanced_stats(self):
        """طباعة الإحصائيات المحسنة"""
        if not self.stats['start_time']:
            return
        
        runtime = datetime.now() - self.stats['start_time']
        performance_stats = self.risk_manager.get_performance_stats()
        
        # معلومات الشبكة
        network_info = self.flash_loan_manager.get_network_info()
        
        stats_message = f\"\"\"
=== إحصائيات برنامج المراجحة المحسن ===
وقت التشغيل: {runtime}
إجمالي الفرص: {self.stats['total_opportunities']}
الصفقات العادية: {self.stats['executed_trades']}
صفقات القروض السريعة: {self.stats['flash_loan_trades']}
إجمالي الربح: {self.stats['total_profit']:.4f} USDT
ربح القروض السريعة: {self.stats['flash_loan_profit']:.4f} USDT
معدل النجاح: {performance_stats.get('success_rate', 0):.2f}%

=== معلومات الشبكة ===
متصل بـ Ethereum: {network_info.get('connected', False)}
رقم الكتلة: {network_info.get('latest_block', 'غير متاح')}
سعر الغاز: {network_info.get('gas_price_gwei', 0):.2f} Gwei
رصيد الحساب: {network_info.get('account_balance_eth', 0):.4f} ETH

آخر تحديث: {self.stats['last_update']}
==========================================
\"\"\"
        
        self.logger.info(stats_message)
    
    async def deploy_flash_loan_contract(self) -> str:
        """نشر عقد القرض السريع"""
        try:
            self.logger.info("نشر عقد القرض السريع...")
            
            contract_address = self.flash_loan_manager.deploy_contract()
            
            if contract_address:
                self.logger.info(f"تم نشر العقد بنجاح: {contract_address}")
                
                # حفظ عنوان العقد
                with open('config/contract_address.json', 'w') as f:
                    json.dump({
                        'flash_loan_contract': contract_address,
                        'deployed_at': datetime.now().isoformat()
                    }, f, indent=2)
                
                return contract_address
            else:
                self.logger.error("فشل في نشر العقد")
                return None
                
        except Exception as e:
            self.logger.error(f"خطأ في نشر العقد: {e}")
            return None
    
    def load_existing_contract(self, contract_address: str) -> bool:
        """تحميل عقد موجود"""
        try:
            success = self.flash_loan_manager.load_contract(contract_address)
            
            if success:
                self.logger.info(f"تم تحميل العقد بنجاح: {contract_address}")
                self.flash_loan_enabled = True
            else:
                self.logger.error("فشل في تحميل العقد")
            
            return success
            
        except Exception as e:
            self.logger.error(f"خطأ في تحميل العقد: {e}")
            return False
    
    def stop(self):
        """إيقاف البرنامج"""
        self.logger.info("إيقاف برنامج المراجحة المحسن...")
        self.running = False
    
    async def cleanup(self):
        """تنظيف الموارد"""
        try:
            self.logger.info("تنظيف الموارد...")
            
            # إغلاق اتصالات المنصات
            self.exchange_manager.close_all_connections()
            
            # حفظ الإحصائيات النهائية
            final_stats = {
                'runtime_stats': self.stats,
                'performance_stats': self.risk_manager.get_performance_stats(),
                'network_info': self.flash_loan_manager.get_network_info(),
                'end_time': datetime.now().isoformat()
            }
            
            with open('logs/enhanced_final_stats.json', 'w', encoding='utf-8') as f:
                json.dump(final_stats, f, ensure_ascii=False, indent=2, default=str)
            
            self.print_enhanced_stats()
            self.logger.info("تم إيقاف البرنامج المحسن بنجاح")
            
        except Exception as e:
            self.logger.error(f"خطأ في التنظيف: {e}")

class EnhancedArbitrageBotCLI:
    """واجهة سطر الأوامر المحسنة"""
    
    def __init__(self):
        self.bot = EnhancedArbitrageBot()
    
    async def run_interactive_mode(self):
        """تشغيل الوضع التفاعلي المحسن"""
        print("=== برنامج مراجحة العملات المشفرة المحسن ===")
        print("الأوامر المتاحة:")
        print("1. start - بدء التشغيل العادي")
        print("2. start-flash - بدء التشغيل مع القروض السريعة")
        print("3. deploy - نشر عقد القرض السريع")
        print("4. load <address> - تحميل عقد موجود")
        print("5. stop - إيقاف التشغيل")
        print("6. stats - عرض الإحصائيات")
        print("7. network - معلومات الشبكة")
        print("8. opportunities - عرض الفرص الحالية")
        print("9. quit - الخروج")
        print("===============================================")
        
        while True:
            try:
                command = input("أدخل الأمر: ").strip().lower()
                
                if command == 'start':
                    if not self.bot.running:
                        print("بدء التشغيل العادي...")
                        asyncio.create_task(self.bot.start(enable_flash_loans=False))
                    else:
                        print("البرنامج يعمل بالفعل")
                
                elif command == 'start-flash':
                    if not self.bot.running:
                        print("بدء التشغيل مع القروض السريعة...")
                        asyncio.create_task(self.bot.start(enable_flash_loans=True))
                    else:
                        print("البرنامج يعمل بالفعل")
                
                elif command == 'deploy':
                    print("نشر عقد القرض السريع...")
                    contract_address = await self.bot.deploy_flash_loan_contract()
                    if contract_address:
                        print(f"تم نشر العقد: {contract_address}")
                    else:
                        print("فشل في نشر العقد")
                
                elif command.startswith('load '):
                    address = command.split(' ', 1)[1]
                    print(f"تحميل العقد: {address}")
                    success = self.bot.load_existing_contract(address)
                    if success:
                        print("تم تحميل العقد بنجاح")
                    else:
                        print("فشل في تحميل العقد")
                
                elif command == 'stop':
                    if self.bot.running:
                        self.bot.stop()
                        print("تم إيقاف البرنامج")
                    else:
                        print("البرنامج متوقف بالفعل")
                
                elif command == 'stats':
                    self.bot.print_enhanced_stats()
                
                elif command == 'network':
                    network_info = self.bot.flash_loan_manager.get_network_info()
                    print("معلومات الشبكة:")
                    for key, value in network_info.items():
                        print(f"  {key}: {value}")
                
                elif command == 'opportunities':
                    await self.show_current_opportunities()
                
                elif command == 'quit':
                    if self.bot.running:
                        self.bot.stop()
                    print("وداعاً!")
                    break
                
                else:
                    print("أمر غير معروف")
                
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\\nتم إيقاف البرنامج")
                if self.bot.running:
                    self.bot.stop()
                break
            except Exception as e:
                print(f"خطأ: {e}")
    
    async def show_current_opportunities(self):
        """عرض الفرص الحالية"""
        try:
            print("جلب الأسعار الحالية...")
            prices = await self.bot.exchange_manager.fetch_all_prices(Config.SUPPORTED_PAIRS)
            
            if not prices:
                print("لا توجد أسعار متاحة")
                return
            
            opportunities = self.bot.exchange_manager.find_arbitrage_opportunities(
                Config.MIN_PROFIT_PERCENTAGE
            )
            
            if not opportunities:
                print("لا توجد فرص مراجحة حالياً")
                return
            
            print(f"\\n=== الفرص الحالية ({len(opportunities)}) ===")
            for i, opp in enumerate(opportunities[:5], 1):
                flash_suitable = "✓" if opp['profit_percentage'] > 1.0 else "✗"
                print(f"{i}. {opp['symbol']} [Flash Loan: {flash_suitable}]")
                print(f"   الشراء من: {opp['buy_exchange']} بسعر {opp['buy_price']:.6f}")
                print(f"   البيع في: {opp['sell_exchange']} بسعر {opp['sell_price']:.6f}")
                print(f"   الربح: {opp['profit_percentage']:.2f}%")
                print()
                
        except Exception as e:
            print(f"خطأ في جلب الفرص: {e}")

async def main():
    """الدالة الرئيسية المحسنة"""
    try:
        cli = EnhancedArbitrageBotCLI()
        await cli.run_interactive_mode()
    except Exception as e:
        print(f"خطأ في التشغيل: {e}")

if __name__ == "__main__":
    asyncio.run(main())

