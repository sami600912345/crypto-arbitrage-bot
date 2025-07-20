"""
ملف التكوين الرئيسي لبرنامج مراجحة العملات المشفرة
"""

import os
from dotenv import load_dotenv
from typing import Dict, List

# تحميل متغيرات البيئة
load_dotenv()

class Config:
    """فئة التكوين الرئيسية"""
    
    # إعدادات API
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')
    
    COINBASE_API_KEY = os.getenv('COINBASE_API_KEY')
    COINBASE_SECRET_KEY = os.getenv('COINBASE_SECRET_KEY')
    
    KRAKEN_API_KEY = os.getenv('KRAKEN_API_KEY')
    KRAKEN_SECRET_KEY = os.getenv('KRAKEN_SECRET_KEY')
    
    # إعدادات Web3
    INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')
    WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
    
    # إعدادات المراجحة
    MIN_PROFIT_PERCENTAGE = float(os.getenv('MIN_PROFIT_PERCENTAGE', 0.5))
    MAX_TRADE_AMOUNT = float(os.getenv('MAX_TRADE_AMOUNT', 1000))
    MIN_TRADE_AMOUNT = float(os.getenv('MIN_TRADE_AMOUNT', 10))
    
    # إعدادات الأمان
    MAX_SLIPPAGE = float(os.getenv('MAX_SLIPPAGE', 2.0))
    STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', 5.0))
    
    # إعدادات قاعدة البيانات
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///arbitrage_bot.db')
    
    # إعدادات Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # إعدادات التسجيل
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/arbitrage_bot.log')
    
    # إعدادات Flash Loans
    AAVE_POOL_ADDRESS = os.getenv('AAVE_POOL_ADDRESS', '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2')
    FLASH_LOAN_FEE = float(os.getenv('FLASH_LOAN_FEE', 0.0005))
    
    # إعدادات الشبكة
    ETHEREUM_RPC_URL = os.getenv('ETHEREUM_RPC_URL')
    POLYGON_RPC_URL = os.getenv('POLYGON_RPC_URL')
    ARBITRUM_RPC_URL = os.getenv('ARBITRUM_RPC_URL')
    
    # المنصات المدعومة
    SUPPORTED_EXCHANGES = [
        'binance',
        'coinbase',
        'kraken',
        'kucoin',
        'huobi'
    ]
    
    # أزواج التداول المدعومة
    SUPPORTED_PAIRS = [
        'BTC/USDT',
        'ETH/USDT',
        'BNB/USDT',
        'ADA/USDT',
        'DOT/USDT',
        'LINK/USDT',
        'UNI/USDT',
        'AAVE/USDT'
    ]
    
    # إعدادات DEX
    DEX_CONFIGS = {
        'uniswap_v2': {
            'router_address': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
            'factory_address': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
        },
        'uniswap_v3': {
            'router_address': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
            'factory_address': '0x1F98431c8aD98523631AE4a59f267346ea31F984'
        },
        'sushiswap': {
            'router_address': '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
            'factory_address': '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac'
        }
    }
    
    # إعدادات المراقبة
    MONITORING_INTERVAL = 5  # ثواني
    PRICE_UPDATE_INTERVAL = 1  # ثواني
    
    @classmethod
    def validate_config(cls) -> bool:
        """التحقق من صحة التكوين"""
        required_fields = [
            'BINANCE_API_KEY',
            'BINANCE_SECRET_KEY',
            'INFURA_PROJECT_ID',
            'PRIVATE_KEY',
            'WALLET_ADDRESS'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"حقول مفقودة في التكوين: {', '.join(missing_fields)}")
            return False
        
        return True
    
    @classmethod
    def get_exchange_config(cls, exchange_name: str) -> Dict:
        """الحصول على تكوين منصة معينة"""
        configs = {
            'binance': {
                'api_key': cls.BINANCE_API_KEY,
                'secret': cls.BINANCE_SECRET_KEY,
                'sandbox': False,
                'rateLimit': 1200,
                'enableRateLimit': True
            },
            'coinbase': {
                'api_key': cls.COINBASE_API_KEY,
                'secret': cls.COINBASE_SECRET_KEY,
                'sandbox': False,
                'rateLimit': 10000,
                'enableRateLimit': True
            },
            'kraken': {
                'api_key': cls.KRAKEN_API_KEY,
                'secret': cls.KRAKEN_SECRET_KEY,
                'sandbox': False,
                'rateLimit': 3000,
                'enableRateLimit': True
            }
        }
        
        return configs.get(exchange_name, {})

