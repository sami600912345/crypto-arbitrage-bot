"""
برنامج مراجحة العملات المشفرة الرئيسي
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

class ArbitrageBot:
    """البرنامج الرئيسي للمراجحة"""
    
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
        
        # متغيرات التحكم
        self.running = False
        self.stats = {
            'start_time': None,
            'total_opportunities': 0,
            'executed_trades': 0,
            'total_profit': 0,
            'last_update': None
        }
        
        # إعداد معالج الإشارات للإغلاق الآمن
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.logger.info("تم تهيئة برنامج المراجحة بنجاح")
    
    def setup_logging(self):
        """إعداد نظام التسجيل"""
        # إنشاء مجلد السجلات إذا لم يكن موجوداً
        import os
        os.makedirs('logs', exist_ok=True)
        
        # تكوين التسجيل
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
    
    async def start(self):
        """بدء تشغيل البرنامج"""
        self.logger.info("بدء تشغيل برنامج المراجحة...")
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        try:
            # حلقة التشغيل الرئيسية
            while self.running:
                await self.run_arbitrage_cycle()
                await asyncio.sleep(Config.MONITORING_INTERVAL)
                
        except Exception as e:
            self.logger.error(f"خطأ في التشغيل الرئيسي: {e}")
        finally:
            await self.cleanup()
    
    async def run_arbitrage_cycle(self):
        """تشغيل دورة مراجحة واحدة"""
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
                
                # معالجة كل فرصة
                for opportunity in opportunities[:3]:  # أفضل 3 فرص فقط
                    await self.process_opportunity(opportunity)
            
            # تحديث الإحصائيات
            self.stats['last_update'] = datetime.now()
            
            # طباعة الإحصائيات كل 10 دورات
            if self.stats['total_opportunities'] % 10 == 0:
                self.print_stats()
                
        except Exception as e:
            self.logger.error(f"خطأ في دورة المراجحة: {e}")
    
    async def process_opportunity(self, opportunity: Dict):
        """معالجة فرصة مراجحة واحدة"""
        try:
            self.logger.info(f"معالجة فرصة: {opportunity['symbol']} - "
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
            
            # تنفيذ الصفقة
            self.logger.info(f"تنفيذ صفقة مراجحة: {opportunity['symbol']} - "
                           f"المبلغ: {trade_amount}")
            
            trade_result = await self.exchange_manager.execute_arbitrage_trade(
                opportunity, trade_amount
            )
            
            # تسجيل النتيجة
            trade_result.update({
                'symbol': opportunity['symbol'],
                'buy_exchange': opportunity['buy_exchange'],
                'sell_exchange': opportunity['sell_exchange'],
                'trade_amount': trade_amount
            })
            
            self.risk_manager.record_trade(trade_result)
            
            if trade_result['success']:
                self.stats['executed_trades'] += 1
                self.stats['total_profit'] += trade_result.get('profit', 0)
                self.logger.info(f"تم تنفيذ الصفقة بنجاح. الربح: {trade_result.get('profit', 0):.4f}")
            else:
                self.logger.error(f"فشل في تنفيذ الصفقة: {trade_result.get('error', 'خطأ غير معروف')}")
            
        except Exception as e:
            self.logger.error(f"خطأ في معالجة الفرصة: {e}")
    
    def print_stats(self):
        """طباعة الإحصائيات"""
        if not self.stats['start_time']:
            return
        
        runtime = datetime.now() - self.stats['start_time']
        performance_stats = self.risk_manager.get_performance_stats()
        
        stats_message = f\"\"\"
=== إحصائيات برنامج المراجحة ===
وقت التشغيل: {runtime}
إجمالي الفرص: {self.stats['total_opportunities']}
الصفقات المنفذة: {self.stats['executed_trades']}
إجمالي الربح: {self.stats['total_profit']:.4f} USDT
معدل النجاح: {performance_stats.get('success_rate', 0):.2f}%
آخر تحديث: {self.stats['last_update']}
=====================================
\"\"\"
        
        self.logger.info(stats_message)
    
    def stop(self):
        """إيقاف البرنامج"""
        self.logger.info("إيقاف برنامج المراجحة...")
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
                'end_time': datetime.now().isoformat()
            }
            
            with open('logs/final_stats.json', 'w', encoding='utf-8') as f:
                json.dump(final_stats, f, ensure_ascii=False, indent=2, default=str)
            
            self.print_stats()
            self.logger.info("تم إيقاف البرنامج بنجاح")
            
        except Exception as e:
            self.logger.error(f"خطأ في التنظيف: {e}")

class ArbitrageBotCLI:
    """واجهة سطر الأوامر للبرنامج"""
    
    def __init__(self):
        self.bot = ArbitrageBot()
    
    async def run_interactive_mode(self):
        """تشغيل الوضع التفاعلي"""
        print("=== برنامج مراجحة العملات المشفرة ===")
        print("الأوامر المتاحة:")
        print("1. start - بدء التشغيل")
        print("2. stop - إيقاف التشغيل")
        print("3. stats - عرض الإحصائيات")
        print("4. opportunities - عرض الفرص الحالية")
        print("5. quit - الخروج")
        print("=====================================")
        
        while True:
            try:
                command = input("أدخل الأمر: ").strip().lower()
                
                if command == 'start':
                    if not self.bot.running:
                        print("بدء تشغيل البرنامج...")
                        asyncio.create_task(self.bot.start())
                    else:
                        print("البرنامج يعمل بالفعل")
                
                elif command == 'stop':
                    if self.bot.running:
                        self.bot.stop()
                        print("تم إيقاف البرنامج")
                    else:
                        print("البرنامج متوقف بالفعل")
                
                elif command == 'stats':
                    self.bot.print_stats()
                
                elif command == 'opportunities':
                    await self.show_current_opportunities()
                
                elif command == 'quit':
                    if self.bot.running:
                        self.bot.stop()
                    print("وداعاً!")
                    break
                
                else:
                    print("أمر غير معروف")
                
                await asyncio.sleep(0.1)  # تجنب استهلاك CPU
                
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
                print(f"{i}. {opp['symbol']}")
                print(f"   الشراء من: {opp['buy_exchange']} بسعر {opp['buy_price']:.6f}")
                print(f"   البيع في: {opp['sell_exchange']} بسعر {opp['sell_price']:.6f}")
                print(f"   الربح: {opp['profit_percentage']:.2f}%")
                print()
                
        except Exception as e:
            print(f"خطأ في جلب الفرص: {e}")

async def main():
    """الدالة الرئيسية"""
    try:
        cli = ArbitrageBotCLI()
        await cli.run_interactive_mode()
    except Exception as e:
        print(f"خطأ في التشغيل: {e}")

if __name__ == "__main__":
    asyncio.run(main())

