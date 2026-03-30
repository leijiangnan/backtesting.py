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
print(stats)

bt.plot()