const { ethers } = require("hardhat");

async function main() {
  console.log("بدء نشر عقد FlashLoanArbitrage...");

  // الحصول على الحساب المنشر
  const [deployer] = await ethers.getSigners();
  console.log("نشر العقد باستخدام الحساب:", deployer.address);

  // التحقق من رصيد الحساب
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("رصيد الحساب:", ethers.formatEther(balance), "ETH");

  // عنوان Aave Pool Address Provider (Mainnet)
  const AAVE_POOL_ADDRESSES_PROVIDER = "0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e";
  
  // في حالة الاختبار على Sepolia
  // const AAVE_POOL_ADDRESSES_PROVIDER = "0x012bAC54348C0E635dCAc9D5FB99f06F24136C9A";

  try {
    // الحصول على factory للعقد
    const FlashLoanArbitrage = await ethers.getContractFactory("FlashLoanArbitrage");
    
    console.log("نشر العقد...");
    
    // نشر العقد
    const flashLoanArbitrage = await FlashLoanArbitrage.deploy(AAVE_POOL_ADDRESSES_PROVIDER);
    
    // انتظار التأكيد
    await flashLoanArbitrage.waitForDeployment();
    
    const contractAddress = await flashLoanArbitrage.getAddress();
    console.log("تم نشر FlashLoanArbitrage على العنوان:", contractAddress);
    
    // حفظ معلومات النشر
    const deploymentInfo = {
      contractAddress: contractAddress,
      deployer: deployer.address,
      network: hre.network.name,
      aavePoolProvider: AAVE_POOL_ADDRESSES_PROVIDER,
      deploymentTime: new Date().toISOString(),
      transactionHash: flashLoanArbitrage.deploymentTransaction().hash
    };
    
    // كتابة معلومات النشر إلى ملف
    const fs = require('fs');
    const path = require('path');
    
    const deploymentPath = path.join(__dirname, '..', 'config', 'deployment.json');
    
    // إنشاء مجلد config إذا لم يكن موجوداً
    const configDir = path.dirname(deploymentPath);
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }
    
    fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
    console.log("تم حفظ معلومات النشر في:", deploymentPath);
    
    // التحقق من العقد
    console.log("التحقق من العقد...");
    
    // التحقق من المالك
    const owner = await flashLoanArbitrage.owner();
    console.log("مالك العقد:", owner);
    
    // التحقق من عنوان Pool
    const poolAddress = await flashLoanArbitrage.POOL();
    console.log("عنوان Aave Pool:", poolAddress);
    
    console.log("تم نشر العقد بنجاح!");
    console.log("عنوان العقد:", contractAddress);
    console.log("تكلفة النشر:", ethers.formatEther(
      (await ethers.provider.getBalance(deployer.address)).toString()
    ), "ETH");
    
    return contractAddress;
    
  } catch (error) {
    console.error("خطأ في نشر العقد:", error);
    process.exit(1);
  }
}

// تشغيل السكريبت
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

