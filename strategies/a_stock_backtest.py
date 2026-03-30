import baostock as bs
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# ============ 1. 获取A股数据 ============
def get_a_stock_data(symbol="sh.600519", start="2020-01-01", end="2025-12-31"):
    """
    用 BaoStock 获取A股数据
    注意代码格式：sh.600519（沪市）、sz.000001（深市）
    """
    bs.login()
    rs = bs.query_history_k_data_plus(
        symbol,
        "date,open,high,low,close,volume",
        start_date=start,
        end_date=end,
        frequency="d",
        adjustflag="2"  # 前复权
    )
    data_list = []
    while rs.next():
        data_list.append(rs.get_row_data())
    bs.logout()

    df = pd.DataFrame(data_list, columns=rs.fields)
    df = df.rename(columns={
        "date": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    })
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col])
    return df

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
# 获取贵州茅台 2020-2025 数据
data = get_a_stock_data("sh.600519", "2020-01-01", "2025-12-31")

bt = Backtest(
    data,
    DualMaCross,
    cash=100_000,          # 初始资金 10万
    commission=0.0003,     # A股佣金万三
    exclusive_orders=True, # 新信号覆盖旧订单
)

# 运行回测
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