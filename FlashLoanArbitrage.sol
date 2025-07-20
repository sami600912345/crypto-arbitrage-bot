// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@aave/core-v3/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@aave/core-v3/contracts/interfaces/IPoolAddressesProvider.sol";
import "@aave/core-v3/contracts/dependencies/openzeppelin/contracts/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

interface IERC20Extended is IERC20 {
    function decimals() external view returns (uint8);
}

interface IUniswapV2Router {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
    
    function getAmountsOut(uint amountIn, address[] calldata path)
        external view returns (uint[] memory amounts);
}

interface ISushiswapRouter {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
    
    function getAmountsOut(uint amountIn, address[] calldata path)
        external view returns (uint[] memory amounts);
}

/**
 * @title FlashLoanArbitrage
 * @dev عقد ذكي لتنفيذ المراجحة باستخدام القروض السريعة من Aave
 */
contract FlashLoanArbitrage is FlashLoanSimpleReceiverBase, Ownable, ReentrancyGuard {
    
    // عناوين الموجهات (Routers)
    address public constant UNISWAP_V2_ROUTER = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
    address public constant SUSHISWAP_ROUTER = 0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F;
    address public constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    
    // إعدادات المراجحة
    uint256 public constant MAX_SLIPPAGE = 300; // 3%
    uint256 public constant SLIPPAGE_BASE = 10000;
    
    // الأحداث
    event ArbitrageExecuted(
        address indexed asset,
        uint256 amount,
        uint256 profit,
        address buyDex,
        address sellDex
    );
    
    event FlashLoanExecuted(
        address indexed asset,
        uint256 amount,
        uint256 premium
    );
    
    event ProfitWithdrawn(
        address indexed asset,
        uint256 amount,
        address indexed to
    );
    
    // الهياكل
    struct ArbitrageParams {
        address tokenA;
        address tokenB;
        uint256 amountIn;
        address buyDex;  // DEX للشراء
        address sellDex; // DEX للبيع
        uint256 minProfit;
    }
    
    // المتغيرات
    mapping(address => bool) public authorizedCallers;
    uint256 public totalProfits;
    mapping(address => uint256) public tokenProfits;
    
    modifier onlyAuthorized() {
        require(authorizedCallers[msg.sender] || msg.sender == owner(), "غير مخول");
        _;
    }
    
    constructor(address _addressProvider) 
        FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_addressProvider)) 
    {
        authorizedCallers[msg.sender] = true;
    }
    
    /**
     * @dev تنفيذ المراجحة باستخدام القرض السريع
     */
    function executeArbitrage(ArbitrageParams calldata params) 
        external 
        onlyAuthorized 
        nonReentrant 
    {
        require(params.amountIn > 0, "المبلغ يجب أن يكون أكبر من صفر");
        require(params.tokenA != address(0) && params.tokenB != address(0), "عناوين الرموز غير صحيحة");
        
        // التحقق من الربحية المحتملة قبل التنفيذ
        uint256 expectedProfit = calculatePotentialProfit(params);
        require(expectedProfit >= params.minProfit, "الربح المتوقع أقل من الحد الأدنى");
        
        // تنفيذ القرض السريع
        bytes memory paramsData = abi.encode(params);
        
        POOL.flashLoanSimple(
            address(this),
            params.tokenA,
            params.amountIn,
            paramsData,
            0
        );
    }
    
    /**
     * @dev تنفيذ العملية بعد استلام القرض السريع
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == address(POOL), "المرسل غير صحيح");
        require(initiator == address(this), "المبادر غير صحيح");
        
        // فك تشفير المعاملات
        ArbitrageParams memory arbParams = abi.decode(params, (ArbitrageParams));
        
        // تنفيذ المراجحة
        uint256 profit = _performArbitrage(arbParams);
        
        // التأكد من وجود ربح كافي لسداد القرض
        uint256 totalOwed = amount + premium;
        require(IERC20(asset).balanceOf(address(this)) >= totalOwed, "رصيد غير كافي لسداد القرض");
        
        // الموافقة على سحب المبلغ المستحق
        IERC20(asset).approve(address(POOL), totalOwed);
        
        // تسجيل الربح
        if (profit > 0) {
            tokenProfits[asset] += profit;
            totalProfits += profit;
        }
        
        emit FlashLoanExecuted(asset, amount, premium);
        
        return true;
    }
    
    /**
     * @dev تنفيذ المراجحة الفعلية
     */
    function _performArbitrage(ArbitrageParams memory params) 
        internal 
        returns (uint256 profit) 
    {
        uint256 initialBalance = IERC20(params.tokenA).balanceOf(address(this));
        
        // الخطوة 1: شراء tokenB باستخدام tokenA من DEX الأول
        uint256 tokenBAmount = _swapTokens(
            params.tokenA,
            params.tokenB,
            params.amountIn,
            params.buyDex
        );
        
        require(tokenBAmount > 0, "فشل في الشراء من DEX الأول");
        
        // الخطوة 2: بيع tokenB للحصول على tokenA من DEX الثاني
        uint256 tokenAReceived = _swapTokens(
            params.tokenB,
            params.tokenA,
            tokenBAmount,
            params.sellDex
        );
        
        require(tokenAReceived > 0, "فشل في البيع في DEX الثاني");
        
        // حساب الربح
        uint256 finalBalance = IERC20(params.tokenA).balanceOf(address(this));
        
        if (finalBalance > initialBalance) {
            profit = finalBalance - initialBalance;
            
            emit ArbitrageExecuted(
                params.tokenA,
                params.amountIn,
                profit,
                params.buyDex,
                params.sellDex
            );
        }
        
        return profit;
    }
    
    /**
     * @dev تبديل الرموز في DEX محدد
     */
    function _swapTokens(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        address dexRouter
    ) internal returns (uint256 amountOut) {
        
        IERC20(tokenIn).approve(dexRouter, amountIn);
        
        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;
        
        uint256 deadline = block.timestamp + 300; // 5 دقائق
        
        if (dexRouter == UNISWAP_V2_ROUTER) {
            uint[] memory amounts = IUniswapV2Router(dexRouter).swapExactTokensForTokens(
                amountIn,
                0, // نقبل أي مبلغ من الرموز
                path,
                address(this),
                deadline
            );
            amountOut = amounts[1];
        } else if (dexRouter == SUSHISWAP_ROUTER) {
            uint[] memory amounts = ISushiswapRouter(dexRouter).swapExactTokensForTokens(
                amountIn,
                0,
                path,
                address(this),
                deadline
            );
            amountOut = amounts[1];
        } else {
            revert("DEX غير مدعوم");
        }
        
        return amountOut;
    }
    
    /**
     * @dev حساب الربح المحتمل قبل التنفيذ
     */
    function calculatePotentialProfit(ArbitrageParams calldata params) 
        public 
        view 
        returns (uint256 expectedProfit) 
    {
        // الحصول على السعر من DEX الأول (الشراء)
        address[] memory buyPath = new address[](2);
        buyPath[0] = params.tokenA;
        buyPath[1] = params.tokenB;
        
        uint256[] memory buyAmounts;
        if (params.buyDex == UNISWAP_V2_ROUTER) {
            buyAmounts = IUniswapV2Router(params.buyDex).getAmountsOut(params.amountIn, buyPath);
        } else if (params.buyDex == SUSHISWAP_ROUTER) {
            buyAmounts = ISushiswapRouter(params.buyDex).getAmountsOut(params.amountIn, buyPath);
        } else {
            return 0;
        }
        
        uint256 tokenBAmount = buyAmounts[1];
        
        // الحصول على السعر من DEX الثاني (البيع)
        address[] memory sellPath = new address[](2);
        sellPath[0] = params.tokenB;
        sellPath[1] = params.tokenA;
        
        uint256[] memory sellAmounts;
        if (params.sellDex == UNISWAP_V2_ROUTER) {
            sellAmounts = IUniswapV2Router(params.sellDex).getAmountsOut(tokenBAmount, sellPath);
        } else if (params.sellDex == SUSHISWAP_ROUTER) {
            sellAmounts = ISushiswapRouter(params.sellDex).getAmountsOut(tokenBAmount, sellPath);
        } else {
            return 0;
        }
        
        uint256 tokenAReceived = sellAmounts[1];
        
        // حساب الربح (مع خصم رسوم القرض السريع)
        if (tokenAReceived > params.amountIn) {
            uint256 grossProfit = tokenAReceived - params.amountIn;
            uint256 flashLoanFee = (params.amountIn * 5) / 10000; // 0.05% رسوم Aave
            
            if (grossProfit > flashLoanFee) {
                expectedProfit = grossProfit - flashLoanFee;
            }
        }
        
        return expectedProfit;
    }
    
    /**
     * @dev سحب الأرباح
     */
    function withdrawProfits(address token, uint256 amount) 
        external 
        onlyOwner 
    {
        require(amount <= tokenProfits[token], "المبلغ أكبر من الأرباح المتاحة");
        
        tokenProfits[token] -= amount;
        IERC20(token).transfer(owner(), amount);
        
        emit ProfitWithdrawn(token, amount, owner());
    }
    
    /**
     * @dev سحب جميع الأرباح لرمز معين
     */
    function withdrawAllProfits(address token) external onlyOwner {
        uint256 amount = tokenProfits[token];
        require(amount > 0, "لا توجد أرباح للسحب");
        
        tokenProfits[token] = 0;
        IERC20(token).transfer(owner(), amount);
        
        emit ProfitWithdrawn(token, amount, owner());
    }
    
    /**
     * @dev إضافة مستخدم مخول
     */
    function addAuthorizedCaller(address caller) external onlyOwner {
        authorizedCallers[caller] = true;
    }
    
    /**
     * @dev إزالة مستخدم مخول
     */
    function removeAuthorizedCaller(address caller) external onlyOwner {
        authorizedCallers[caller] = false;
    }
    
    /**
     * @dev سحب الرموز في حالة الطوارئ
     */
    function emergencyWithdraw(address token) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        if (balance > 0) {
            IERC20(token).transfer(owner(), balance);
        }
    }
    
    /**
     * @dev الحصول على رصيد رمز معين
     */
    function getTokenBalance(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }
    
    /**
     * @dev التحقق من إمكانية تنفيذ المراجحة
     */
    function canExecuteArbitrage(ArbitrageParams calldata params) 
        external 
        view 
        returns (bool canExecute, uint256 expectedProfit, string memory reason) 
    {
        // التحقق من صحة المعاملات
        if (params.amountIn == 0) {
            return (false, 0, "المبلغ يجب أن يكون أكبر من صفر");
        }
        
        if (params.tokenA == address(0) || params.tokenB == address(0)) {
            return (false, 0, "عناوين الرموز غير صحيحة");
        }
        
        if (params.buyDex == params.sellDex) {
            return (false, 0, "يجب أن تكون منصات التداول مختلفة");
        }
        
        // حساب الربح المتوقع
        expectedProfit = calculatePotentialProfit(params);
        
        if (expectedProfit < params.minProfit) {
            return (false, expectedProfit, "الربح المتوقع أقل من الحد الأدنى");
        }
        
        return (true, expectedProfit, "يمكن تنفيذ المراجحة");
    }
}

