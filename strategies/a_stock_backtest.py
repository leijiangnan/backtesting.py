import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG

# ============ 2. 定义策略 ============
class DualMaCross(Strategy):
    """双均线交叉策略"""
    fast_period = 10   # 短期均线周期
    slow_period = 30   # 长期均线周期

    def init(self):
        close = self.data.Close
        self.fast_ma = self.I(
            lambda x: pd.Series(x).rolling(self.fast_period).mean(), close
        )
        self.slow_ma = self.I(
            lambda x: pd.Series(x).rolling(self.slow_period).mean(), close
        )

    def next(self):
        # 金叉：短期均线上穿长期均线 → 买入
        if crossover(self.fast_ma, self.slow_ma):
            self.buy()
        # 死叉：短期均线下穿长期均线 → 卖出
        elif crossover(self.slow_ma, self.fast_ma):
            self.position.close()

# ============ 3. 执行回测 ============
data = GOOG

bt = Backtest(
    data,
    DualMaCross,
    cash=100_000,
    commission=0.002,
    exclusive_orders=True,
)

stats = bt.run()

STATS_NAMES = {
    "Start": "开始日期",
    "End": "结束日期",
    "Duration": "持仓时长",
    "Exposure Time [%]": "持仓时间占比 [%]",
    "Equity Final [$]": "最终资金 [$]",
    "Equity Peak [$]": "资金峰值 [$]",
    "Commissions [$]": "佣金 [$]",
    "Return [%]": "收益率 [%]",
    "Buy & Hold Return [%]": "买入持有收益率 [%]",
    "Return (Ann.) [%]": "年化收益率 [%]",
    "Volatility (Ann.) [%]": "年化波动率 [%]",
    "CAGR [%]": "年复合增长率 [%]",
    "Sharpe Ratio": "夏普比率",
    "Sortino Ratio": "索提诺比率",
    "Calmar Ratio": "卡玛比率",
    "Alpha [%]": "阿尔法 [%]",
    "Beta": "贝塔",
    "Max. Drawdown [%]": "最大回撤 [%]",
    "Avg. Drawdown [%]": "平均回撤 [%]",
    "Max. Drawdown Duration": "最大回撤时长",
    "Avg. Drawdown Duration": "平均回撤时长",
    "# Trades": "交易次数",
    "Win Rate [%]": "胜率 [%]",
    "Best Trade [%]": "最佳交易 [%]",
    "Worst Trade [%]": "最差交易 [%]",
    "Avg. Trade [%]": "平均交易 [%]",
    "Max. Trade Duration": "最大交易时长",
    "Avg. Trade Duration": "平均交易时长",
    "Profit Factor": "盈亏比",
    "Expectancy [%]": "期望值 [%]",
    "SQN": "SQN (系统质量指数)",
    "Kelly Criterion": "凯利准则",
    "_strategy": "策略",
}

for key, value in stats.items():
    if key.startswith("_"):
        continue
    cn_name = STATS_NAMES.get(key, key)
    if isinstance(value, float):
        print(f"{cn_name}: {value:.2f}")
    else:
        print(f"{cn_name}: {value}")

# bt.plot()