"""
مدير القروض السريعة للتفاعل مع العقود الذكية
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from web3 import Web3
from web3.contract import Contract
from eth_account import Account
import asyncio
from datetime import datetime

from config import Config

class FlashLoanManager:
    """مدير القروض السريعة"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.w3 = None
        self.account = None
        self.contract = None
        self.contract_address = None
        
        # عناوين الرموز الشائعة على Ethereum
        self.token_addresses = {
            'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
            'USDC': '0xA0b86a33E6417c8C4c7c5c4c4c4c4c4c4c4c4c4c',
            'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
            'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
            'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
        }
        
        # عناوين DEX routers
        self.dex_routers = {
            'uniswap_v2': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
            'sushiswap': '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'
        }
        
        self._initialize_web3()
    
    def _initialize_web3(self):
        """تهيئة اتصال Web3"""
        try:
            if not Config.ETHEREUM_RPC_URL:
                self.logger.error("عنوان RPC غير محدد")
                return
            
            self.w3 = Web3(Web3.HTTPProvider(Config.ETHEREUM_RPC_URL))
            
            if not self.w3.is_connected():
                self.logger.error("فشل في الاتصال بشبكة Ethereum")
                return
            
            # تحميل الحساب
            if Config.PRIVATE_KEY:
                self.account = Account.from_key(Config.PRIVATE_KEY)
                self.logger.info(f"تم تحميل الحساب: {self.account.address}")
            
            self.logger.info("تم تهيئة Web3 بنجاح")
            
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة Web3: {e}")
    
    def deploy_contract(self, constructor_args: List = None) -> Optional[str]:
        """نشر العقد الذكي"""
        try:
            if not self.w3 or not self.account:
                self.logger.error("Web3 أو الحساب غير مهيأ")
                return None
            
            # قراءة ملف العقد المترجم (يجب ترجمته أولاً)
            contract_path = "../contracts/FlashLoanArbitrage.json"
            
            try:
                with open(contract_path, 'r') as f:
                    contract_data = json.load(f)
            except FileNotFoundError:
                self.logger.error("ملف العقد المترجم غير موجود. يرجى ترجمة العقد أولاً")
                return None
            
            # إنشاء العقد
            contract = self.w3.eth.contract(
                abi=contract_data['abi'],
                bytecode=contract_data['bytecode']
            )
            
            # تحضير المعاملة
            constructor_args = constructor_args or [Config.AAVE_POOL_ADDRESS]
            
            transaction = contract.constructor(*constructor_args).build_transaction({
                'from': self.account.address,
                'gas': 3000000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # توقيع وإرسال المعاملة
            signed_txn = self.w3.eth.account.sign_transaction(transaction, Config.PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # انتظار التأكيد
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 1:
                self.contract_address = tx_receipt.contractAddress
                self.logger.info(f"تم نشر العقد بنجاح: {self.contract_address}")
                
                # تحميل العقد
                self.contract = self.w3.eth.contract(
                    address=self.contract_address,
                    abi=contract_data['abi']
                )
                
                return self.contract_address
            else:
                self.logger.error("فشل في نشر العقد")
                return None
                
        except Exception as e:
            self.logger.error(f"خطأ في نشر العقد: {e}")
            return None
    
    def load_contract(self, contract_address: str, abi_path: str = None) -> bool:
        """تحميل عقد موجود"""
        try:
            if not self.w3:
                self.logger.error("Web3 غير مهيأ")
                return False
            
            # تحميل ABI
            if abi_path:
                with open(abi_path, 'r') as f:
                    contract_data = json.load(f)
                    abi = contract_data['abi']
            else:
                # استخدام ABI افتراضي مبسط
                abi = self._get_default_abi()
            
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=abi
            )
            
            self.contract_address = contract_address
            self.logger.info(f"تم تحميل العقد: {contract_address}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في تحميل العقد: {e}")
            return False
    
    async def execute_flash_loan_arbitrage(
        self,
        token_a: str,
        token_b: str,
        amount: int,
        buy_dex: str,
        sell_dex: str,
        min_profit: int = 0
    ) -> Dict:
        """تنفيذ مراجحة باستخدام القرض السريع"""
        try:
            if not self.contract or not self.account:
                return {'success': False, 'error': 'العقد أو الحساب غير مهيأ'}
            
            # تحضير معاملات المراجحة
            arbitrage_params = {
                'tokenA': Web3.to_checksum_address(self.token_addresses.get(token_a, token_a)),
                'tokenB': Web3.to_checksum_address(self.token_addresses.get(token_b, token_b)),
                'amountIn': amount,
                'buyDex': Web3.to_checksum_address(self.dex_routers.get(buy_dex, buy_dex)),
                'sellDex': Web3.to_checksum_address(self.dex_routers.get(sell_dex, sell_dex)),
                'minProfit': min_profit
            }
            
            # التحقق من إمكانية التنفيذ
            can_execute, expected_profit, reason = await self._can_execute_arbitrage(arbitrage_params)
            
            if not can_execute:
                return {'success': False, 'error': reason, 'expected_profit': expected_profit}
            
            # تحضير المعاملة
            transaction = self.contract.functions.executeArbitrage(
                (
                    arbitrage_params['tokenA'],
                    arbitrage_params['tokenB'],
                    arbitrage_params['amountIn'],
                    arbitrage_params['buyDex'],
                    arbitrage_params['sellDex'],
                    arbitrage_params['minProfit']
                )
            ).build_transaction({
                'from': self.account.address,
                'gas': 1000000,  # حد الغاز
                'gasPrice': await self._get_optimal_gas_price(),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # توقيع وإرسال المعاملة
            signed_txn = self.w3.eth.account.sign_transaction(transaction, Config.PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            self.logger.info(f"تم إرسال معاملة القرض السريع: {tx_hash.hex()}")
            
            # انتظار التأكيد
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt.status == 1:
                # تحليل الأحداث
                events = self._parse_transaction_events(tx_receipt)
                
                return {
                    'success': True,
                    'tx_hash': tx_hash.hex(),
                    'gas_used': tx_receipt.gasUsed,
                    'events': events,
                    'expected_profit': expected_profit
                }
            else:
                return {
                    'success': False,
                    'error': 'فشلت المعاملة',
                    'tx_hash': tx_hash.hex()
                }
                
        except Exception as e:
            self.logger.error(f"خطأ في تنفيذ القرض السريع: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _can_execute_arbitrage(self, params: Dict) -> Tuple[bool, int, str]:
        """التحقق من إمكانية تنفيذ المراجحة"""
        try:
            if not self.contract:
                return False, 0, "العقد غير محمل"
            
            result = self.contract.functions.canExecuteArbitrage(
                (
                    params['tokenA'],
                    params['tokenB'],
                    params['amountIn'],
                    params['buyDex'],
                    params['sellDex'],
                    params['minProfit']
                )
            ).call()
            
            can_execute, expected_profit, reason = result
            return can_execute, expected_profit, reason
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من إمكانية التنفيذ: {e}")
            return False, 0, str(e)
    
    async def _get_optimal_gas_price(self) -> int:
        """الحصول على سعر الغاز الأمثل"""
        try:
            # الحصول على سعر الغاز الحالي
            gas_price = self.w3.eth.gas_price
            
            # زيادة 10% للتأكد من التنفيذ السريع
            optimal_price = int(gas_price * 1.1)
            
            return optimal_price
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على سعر الغاز: {e}")
            return self.w3.to_wei('20', 'gwei')  # سعر افتراضي
    
    def _parse_transaction_events(self, tx_receipt) -> List[Dict]:
        """تحليل أحداث المعاملة"""
        events = []
        
        try:
            if not self.contract:
                return events
            
            # تحليل أحداث المراجحة
            arbitrage_events = self.contract.events.ArbitrageExecuted().process_receipt(tx_receipt)
            for event in arbitrage_events:
                events.append({
                    'type': 'ArbitrageExecuted',
                    'asset': event.args.asset,
                    'amount': event.args.amount,
                    'profit': event.args.profit,
                    'buyDex': event.args.buyDex,
                    'sellDex': event.args.sellDex
                })
            
            # تحليل أحداث القرض السريع
            flash_loan_events = self.contract.events.FlashLoanExecuted().process_receipt(tx_receipt)
            for event in flash_loan_events:
                events.append({
                    'type': 'FlashLoanExecuted',
                    'asset': event.args.asset,
                    'amount': event.args.amount,
                    'premium': event.args.premium
                })
                
        except Exception as e:
            self.logger.error(f"خطأ في تحليل الأحداث: {e}")
        
        return events
    
    def get_contract_balance(self, token_address: str) -> int:
        """الحصول على رصيد العقد"""
        try:
            if not self.contract:
                return 0
            
            balance = self.contract.functions.getTokenBalance(
                Web3.to_checksum_address(token_address)
            ).call()
            
            return balance
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على الرصيد: {e}")
            return 0
    
    def withdraw_profits(self, token_address: str, amount: int) -> Dict:
        """سحب الأرباح من العقد"""
        try:
            if not self.contract or not self.account:
                return {'success': False, 'error': 'العقد أو الحساب غير مهيأ'}
            
            transaction = self.contract.functions.withdrawProfits(
                Web3.to_checksum_address(token_address),
                amount
            ).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, Config.PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': tx_receipt.status == 1,
                'tx_hash': tx_hash.hex(),
                'gas_used': tx_receipt.gasUsed
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في سحب الأرباح: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_token_profits(self, token_address: str) -> int:
        """الحصول على أرباح رمز معين"""
        try:
            if not self.contract:
                return 0
            
            profits = self.contract.functions.tokenProfits(
                Web3.to_checksum_address(token_address)
            ).call()
            
            return profits
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على الأرباح: {e}")
            return 0
    
    def _get_default_abi(self) -> List:
        """الحصول على ABI افتراضي مبسط"""
        return [
            {
                "inputs": [{"type": "tuple", "name": "params"}],
                "name": "executeArbitrage",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"type": "tuple", "name": "params"}],
                "name": "canExecuteArbitrage",
                "outputs": [
                    {"type": "bool", "name": "canExecute"},
                    {"type": "uint256", "name": "expectedProfit"},
                    {"type": "string", "name": "reason"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"type": "address", "name": "token"}],
                "name": "getTokenBalance",
                "outputs": [{"type": "uint256", "name": "balance"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def estimate_gas_cost(self, token_a: str, amount: int) -> Dict:
        """تقدير تكلفة الغاز للمعاملة"""
        try:
            if not self.w3:
                return {'success': False, 'error': 'Web3 غير مهيأ'}
            
            # تقدير الغاز للقرض السريع
            estimated_gas = 800000  # تقدير تقريبي
            gas_price = self.w3.eth.gas_price
            
            total_cost_wei = estimated_gas * gas_price
            total_cost_eth = self.w3.from_wei(total_cost_wei, 'ether')
            
            return {
                'success': True,
                'estimated_gas': estimated_gas,
                'gas_price_gwei': self.w3.from_wei(gas_price, 'gwei'),
                'total_cost_wei': total_cost_wei,
                'total_cost_eth': float(total_cost_eth)
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في تقدير تكلفة الغاز: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_network_info(self) -> Dict:
        """الحصول على معلومات الشبكة"""
        try:
            if not self.w3:
                return {}
            
            return {
                'connected': self.w3.is_connected(),
                'chain_id': self.w3.eth.chain_id,
                'latest_block': self.w3.eth.block_number,
                'gas_price_gwei': float(self.w3.from_wei(self.w3.eth.gas_price, 'gwei')),
                'account_address': self.account.address if self.account else None,
                'account_balance_eth': float(self.w3.from_wei(
                    self.w3.eth.get_balance(self.account.address), 'ether'
                )) if self.account else 0
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على معلومات الشبكة: {e}")
            return {}

