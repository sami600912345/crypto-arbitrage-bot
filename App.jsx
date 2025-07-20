import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert.jsx'
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  Zap, 
  Shield, 
  AlertTriangle,
  Play,
  Pause,
  Settings,
  BarChart3,
  Wallet,
  Network,
  Clock
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import './App.css'

function App() {
  const [isRunning, setIsRunning] = useState(false)
  const [flashLoanEnabled, setFlashLoanEnabled] = useState(false)
  const [stats, setStats] = useState({
    totalProfit: 1247.83,
    totalTrades: 156,
    successRate: 87.2,
    activeOpportunities: 3,
    flashLoanTrades: 12,
    flashLoanProfit: 892.45
  })

  const [opportunities, setOpportunities] = useState([
    {
      id: 1,
      symbol: 'BTC/USDT',
      buyExchange: 'Binance',
      sellExchange: 'Kraken',
      buyPrice: 43125.50,
      sellPrice: 43287.25,
      profitPercentage: 0.37,
      profitAmount: 161.75,
      flashLoanSuitable: false,
      timestamp: new Date().toISOString()
    },
    {
      id: 2,
      symbol: 'ETH/USDT',
      buyExchange: 'KuCoin',
      sellExchange: 'Huobi',
      buyPrice: 2651.80,
      sellPrice: 2678.45,
      profitPercentage: 1.00,
      profitAmount: 26.65,
      flashLoanSuitable: true,
      timestamp: new Date().toISOString()
    },
    {
      id: 3,
      symbol: 'ADA/USDT',
      buyExchange: 'Binance',
      sellExchange: 'Coinbase',
      buyPrice: 0.4521,
      sellExchange: 'Kraken',
      sellPrice: 0.4547,
      profitPercentage: 0.57,
      profitAmount: 0.0026,
      flashLoanSuitable: false,
      timestamp: new Date().toISOString()
    }
  ])

  const [profitHistory] = useState([
    { time: '00:00', profit: 0, cumulative: 0 },
    { time: '04:00', profit: 125.50, cumulative: 125.50 },
    { time: '08:00', profit: 89.25, cumulative: 214.75 },
    { time: '12:00', profit: 234.80, cumulative: 449.55 },
    { time: '16:00', profit: 156.75, cumulative: 606.30 },
    { time: '20:00', profit: 198.45, cumulative: 804.75 },
    { time: '24:00', profit: 443.08, cumulative: 1247.83 }
  ])

  const [networkInfo] = useState({
    connected: true,
    chainId: 1,
    blockNumber: 18750234,
    gasPrice: 23.5,
    accountBalance: 2.847
  })

  const handleStart = () => {
    setIsRunning(true)
  }

  const handleStop = () => {
    setIsRunning(false)
  }

  const handleFlashLoanToggle = () => {
    setFlashLoanEnabled(!flashLoanEnabled)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">
              لوحة تحكم مراجحة العملات المشفرة
            </h1>
            <p className="text-slate-300">
              نظام متقدم للمراجحة مع دعم القروض السريعة
            </p>
          </div>
          <div className="flex gap-4">
            <Button
              onClick={isRunning ? handleStop : handleStart}
              className={`${
                isRunning 
                  ? 'bg-red-600 hover:bg-red-700' 
                  : 'bg-green-600 hover:bg-green-700'
              } text-white px-6 py-3`}
            >
              {isRunning ? (
                <>
                  <Pause className="w-4 h-4 mr-2" />
                  إيقاف
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  تشغيل
                </>
              )}
            </Button>
            <Button
              onClick={handleFlashLoanToggle}
              variant={flashLoanEnabled ? "default" : "outline"}
              className="px-6 py-3"
            >
              <Zap className="w-4 h-4 mr-2" />
              القروض السريعة
            </Button>
          </div>
        </div>

        {/* Status Alert */}
        {isRunning && (
          <Alert className="mb-6 bg-green-900/20 border-green-500/50">
            <Activity className="h-4 w-4 text-green-400" />
            <AlertTitle className="text-green-400">النظام يعمل</AlertTitle>
            <AlertDescription className="text-green-300">
              يتم مراقبة {opportunities.length} فرصة مراجحة حالياً
              {flashLoanEnabled && " مع تفعيل القروض السريعة"}
            </AlertDescription>
          </Alert>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">
                إجمالي الربح
              </CardTitle>
              <DollarSign className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                ${stats.totalProfit.toLocaleString()}
              </div>
              <p className="text-xs text-green-400 flex items-center mt-1">
                <TrendingUp className="w-3 h-3 mr-1" />
                +12.5% من الأمس
              </p>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">
                إجمالي الصفقات
              </CardTitle>
              <BarChart3 className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {stats.totalTrades}
              </div>
              <p className="text-xs text-slate-400 mt-1">
                {stats.flashLoanTrades} صفقة قرض سريع
              </p>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">
                معدل النجاح
              </CardTitle>
              <Shield className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {stats.successRate}%
              </div>
              <Progress value={stats.successRate} className="mt-2" />
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">
                الفرص النشطة
              </CardTitle>
              <Activity className="h-4 w-4 text-orange-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {stats.activeOpportunities}
              </div>
              <p className="text-xs text-orange-400 mt-1">
                {opportunities.filter(o => o.flashLoanSuitable).length} مناسبة للقروض السريعة
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="opportunities" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-slate-800/50">
            <TabsTrigger value="opportunities" className="text-white">
              الفرص الحالية
            </TabsTrigger>
            <TabsTrigger value="analytics" className="text-white">
              التحليلات
            </TabsTrigger>
            <TabsTrigger value="network" className="text-white">
              معلومات الشبكة
            </TabsTrigger>
            <TabsTrigger value="settings" className="text-white">
              الإعدادات
            </TabsTrigger>
          </TabsList>

          {/* Opportunities Tab */}
          <TabsContent value="opportunities" className="space-y-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">فرص المراجحة الحالية</CardTitle>
                <CardDescription className="text-slate-300">
                  الفرص المتاحة حالياً مرتبة حسب الربحية
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {opportunities.map((opp) => (
                    <div
                      key={opp.id}
                      className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg border border-slate-600"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="text-lg font-semibold text-white">
                          {opp.symbol}
                        </div>
                        <div className="text-sm text-slate-300">
                          {opp.buyExchange} → {opp.sellExchange}
                        </div>
                        {opp.flashLoanSuitable && (
                          <Badge className="bg-yellow-600 text-yellow-100">
                            <Zap className="w-3 h-3 mr-1" />
                            قرض سريع
                          </Badge>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-green-400">
                          +{opp.profitPercentage}%
                        </div>
                        <div className="text-sm text-slate-400">
                          ${opp.profitAmount.toFixed(2)}
                        </div>
                      </div>
                      <div className="text-right text-xs text-slate-500">
                        <div>شراء: ${opp.buyPrice.toLocaleString()}</div>
                        <div>بيع: ${opp.sellPrice.toLocaleString()}</div>
                      </div>
                      <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                        تنفيذ
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">تطور الأرباح</CardTitle>
                  <CardDescription className="text-slate-300">
                    الأرباح التراكمية خلال آخر 24 ساعة
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={profitHistory}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="time" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1F2937', 
                          border: '1px solid #374151',
                          borderRadius: '8px'
                        }}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="cumulative" 
                        stroke="#10B981" 
                        fill="#10B981" 
                        fillOpacity={0.3}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">أداء القروض السريعة</CardTitle>
                  <CardDescription className="text-slate-300">
                    مقارنة بين الصفقات العادية والقروض السريعة
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">الصفقات العادية</span>
                      <div className="text-right">
                        <div className="text-white font-semibold">
                          {stats.totalTrades - stats.flashLoanTrades}
                        </div>
                        <div className="text-sm text-slate-400">
                          ${(stats.totalProfit - stats.flashLoanProfit).toFixed(2)}
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">القروض السريعة</span>
                      <div className="text-right">
                        <div className="text-white font-semibold">
                          {stats.flashLoanTrades}
                        </div>
                        <div className="text-sm text-yellow-400">
                          ${stats.flashLoanProfit.toFixed(2)}
                        </div>
                      </div>
                    </div>
                    <div className="pt-4 border-t border-slate-600">
                      <div className="text-sm text-slate-400 mb-2">
                        متوسط الربح لكل صفقة
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-300">عادية:</span>
                        <span className="text-white">
                          ${((stats.totalProfit - stats.flashLoanProfit) / (stats.totalTrades - stats.flashLoanTrades)).toFixed(2)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-300">قرض سريع:</span>
                        <span className="text-yellow-400">
                          ${(stats.flashLoanProfit / stats.flashLoanTrades).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Network Tab */}
          <TabsContent value="network" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Network className="w-5 h-5 mr-2" />
                    حالة الشبكة
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">الحالة</span>
                      <Badge className={networkInfo.connected ? "bg-green-600" : "bg-red-600"}>
                        {networkInfo.connected ? "متصل" : "غير متصل"}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">Chain ID</span>
                      <span className="text-white">{networkInfo.chainId}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">رقم الكتلة</span>
                      <span className="text-white">{networkInfo.blockNumber.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">سعر الغاز</span>
                      <span className="text-white">{networkInfo.gasPrice} Gwei</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Wallet className="w-5 h-5 mr-2" />
                    معلومات المحفظة
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">رصيد ETH</span>
                      <span className="text-white">{networkInfo.accountBalance} ETH</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300">القيمة بالدولار</span>
                      <span className="text-green-400">
                        ${(networkInfo.accountBalance * 3000).toFixed(2)}
                      </span>
                    </div>
                    <div className="pt-4 border-t border-slate-600">
                      <Button className="w-full bg-blue-600 hover:bg-blue-700">
                        عرض تفاصيل المحفظة
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Settings className="w-5 h-5 mr-2" />
                  إعدادات النظام
                </CardTitle>
                <CardDescription className="text-slate-300">
                  تكوين معاملات المراجحة والأمان
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-white">إعدادات المراجحة</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">الحد الأدنى للربح</span>
                        <span className="text-white">0.5%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">الحد الأقصى للصفقة</span>
                        <span className="text-white">$1,000</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">الحد الأقصى للانزلاق</span>
                        <span className="text-white">2.0%</span>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-white">إعدادات الأمان</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">الحد الأقصى للخسائر اليومية</span>
                        <span className="text-white">$1,000</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">الحد الأقصى للصفقات اليومية</span>
                        <span className="text-white">100</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">إيقاف الخسارة</span>
                        <span className="text-white">5.0%</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mt-6 pt-6 border-t border-slate-600">
                  <Button className="bg-blue-600 hover:bg-blue-700 mr-4">
                    حفظ الإعدادات
                  </Button>
                  <Button variant="outline">
                    إعادة تعيين
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

