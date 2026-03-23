# 定时任务与数据流水线

## 一、Cron 调度配置（Docker 环境）

定义在 `docker/Dockerfile` 中：

```cron
# min hour day month weekday command
*/30 9,10,11,13,14,15 * * 1-5   /bin/run-parts /etc/cron.hourly      # 盘中刷新
30   17                * * 1-5   /bin/run-parts /etc/cron.workdayly   # 收盘后主任务
30   10                * * 3,6   /bin/run-parts /etc/cron.monthly     # 月度维护
```

| 任务 | 周期 | 时间 | 脚本 | 说明 |
|------|------|------|------|------|
| 盘中刷新 | 每 30 分钟 | 周一至周五 9:00~15:30 | `cron.hourly/run_hourly` | 刷新实时行情数据 |
| 收盘后主任务 | 每工作日 | 周一至周五 17:30 | `cron.workdayly/run_workdayly` | 运行完整数据流水线 |
| 月度维护 | 每周两次 | 周三、周六 10:30 | `cron.monthly/run_monthly` | 清除历史K线缓存目录 |

---

## 二、盘中刷新任务 — `basic_data_daily_job`

**触发方式**：`cron.hourly` → `uv run instock-job basic_data_daily_job`
**触发频率**：交易日 9:00~15:30 每 30 分钟
**用途**：反复刷新股票和 ETF 的实时行情快照

| 顺序 | 函数 | 写入表 | 说明 |
|------|------|--------|------|
| 1 | `save_nph_stock_spot_data` | `cn_stock_spot` | A 股实时行情（~4500+ 只） |
| 2 | `save_nph_etf_spot_data` | `cn_etf_spot` | ETF 基金实时行情 |

**数据来源**：东方财富实时行情接口 `stock_zh_a_spot_em()`

---

## 三、收盘后主任务 — `execute_daily_job`

**触发方式**：`cron.workdayly` → `uv run instock-job execute_daily_job`
**触发时间**：每工作日 17:30
**用途**：收盘后运行完整的数据处理流水线

### 执行流程

```
第1步 [串行] init_job
  │   检查数据库是否存在，不存在则创建
  │
第2.1步 [串行] basic_data_daily_job
  │   拉取当日股票/ETF实时行情，写入 cn_stock_spot / cn_etf_spot
  │
第2.2步 [串行] selection_data_daily_job
  │   拉取综合选股数据，写入 cn_stock_selection
  │
  │   ┌───────────────── 以下4个任务并行执行 ─────────────────┐
  │   │                                                       │
  │   │  第3.1步 basic_data_other_daily_job                   │
  │   │    龙虎榜、资金流向、分红、涨停原因等                     │
  │   │                                                       │
  │   │  第3.2步 indicators_data_daily_job                    │
  │   │    技术指标计算（KDJ、RSI、MACD等）                      │
  │   │                                                       │
  │   │  第4步 klinepattern_data_daily_job                    │
  │   │    K线形态识别（talib 61种形态）                         │
  │   │                                                       │
  │   │  第5步 strategy_data_daily_job                        │
  │   │    10种选股策略筛选（内部也并行执行）                      │
  │   │                                                       │
  │   └───────────────────────────────────────────────────────┘
  │
第6步 [串行] backtest_data_daily_job
  │   回测：为策略/指标表中的历史记录补充 N 日收益率
  │
第7步 [串行] basic_data_after_close_daily_job
      拉取仅收盘后可用的数据（大宗交易、尾盘抢筹）
```

### 第1步 — init_job

| 函数 | 说明 |
|------|------|
| `check_database` / `create_new_database` | 检查数据库 `instockdb` 是否存在，不存在则创建。同时创建 `cn_stock_attention` 基础表 |

### 第2.1步 — basic_data_daily_job

| 顺序 | 函数 | 写入表 | 说明 |
|------|------|--------|------|
| 1 | `save_nph_stock_spot_data` | `cn_stock_spot` | A 股实时行情 |
| 2 | `save_nph_etf_spot_data` | `cn_etf_spot` | ETF 实时行情 |

### 第2.2步 — selection_data_daily_job

| 顺序 | 函数 | 写入表 | 说明 |
|------|------|--------|------|
| 1 | `save_nph_stock_selection_data` | `cn_stock_selection` | 东方财富选股器数据（~4300 只） |

### 第3.1步 — basic_data_other_daily_job（并行）

| 顺序 | 函数 | 写入表 | 说明 |
|------|------|--------|------|
| 1 | `save_nph_stock_lhb_data` | `cn_stock_lhb` | 龙虎榜（东方财富） |
| 2 | `save_nph_stock_top_data` | `cn_stock_top` | 龙虎榜（新浪） |
| 3 | `save_nph_stock_bonus` | `cn_stock_bonus` | 分红配送 |
| 4 | `save_nph_stock_fund_flow_data` | `cn_stock_fund_flow` | 个股资金流向（今日/3日/5日/10日） |
| 5 | `save_nph_stock_sector_fund_flow_data` | `cn_stock_fund_flow_industry` | 行业板块资金流向 |
|   |                                        | `cn_stock_fund_flow_concept` | 概念板块资金流向 |
| 6 | `stock_chip_race_open_data` | `cn_stock_chip_race_open` | 早盘抢筹 |
| 7 | `stock_imitup_reason_data` | `cn_stock_limitup_reason` | 涨停原因揭密 |
| * | `stock_spot_buy`（附带调用） | `cn_stock_spot_buy` | 基本面选股（PE<=20, ROE>=15 等） |

> 注：`stock_spot_buy` 被 `save_nph_stock_lhb_data` 和 `save_nph_stock_top_data` 在末尾附带调用。

### 第3.2步 — indicators_data_daily_job（并行）

| 顺序 | 函数 | 写入表 | 说明 |
|------|------|--------|------|
| 1 | `prepare` | `cn_stock_indicators` | 技术指标（KDJ/RSI/MACD/BOLL/CR/WR/VR/CCI 等） |
| 2 | `guess_buy` | `cn_stock_indicators_buy` | 指标买入信号筛选（KDJ>=80, RSI>=80, CCI>=100 等） |
| 3 | `guess_sell` | `cn_stock_indicators_sell` | 指标卖出信号筛选（KDJ<20, RSI<20, CCI<-100 等） |

### 第4步 — klinepattern_data_daily_job（并行）

| 顺序 | 函数 | 写入表 | 说明 |
|------|------|--------|------|
| 1 | `prepare` | `cn_stock_pattern` | 61 种 K 线形态识别（talib CDL 系列函数） |

### 第5步 — strategy_data_daily_job（并行，内部 10 个策略也并行）

| 策略 | 写入表 | 说明 |
|------|--------|------|
| `enter.check_volume` | `cn_stock_strategy_enter` | 放量上涨 |
| `keep_increasing.check` | `cn_stock_strategy_keep_increasing` | 均线多头（MA30 持续上升） |
| `parking_apron.check` | `cn_stock_strategy_parking_apron` | 停机坪（涨停后高位横盘） |
| `backtrace_ma250.check` | `cn_stock_strategy_backtrace_ma250` | 回踩年线 |
| `breakthrough_platform.check` | `cn_stock_strategy_breakthrough_platform` | 突破平台（突破 MA60） |
| `low_backtrace_increase.check` | `cn_stock_strategy_low_backtrace_increase` | 无大幅回撤 |
| `turtle_trade.check_enter` | `cn_stock_strategy_turtle_trade` | 海龟交易法则 |
| `high_tight_flag.check_high_tight` | `cn_stock_strategy_high_tight_flag` | 高而窄的旗形 |
| `climax_limitdown.check` | `cn_stock_strategy_climax_limitdown` | 放量跌停 |
| `low_atr.check_low_increase` | `cn_stock_strategy_low_atr` | 低 ATR 成长 |

### 第6步 — backtest_data_daily_job

| 函数 | 作用 |
|------|------|
| `prepare` | 遍历以下表中尚未回测的记录，补充 N 日（1/2/3/5/10/20/30/60）收益率 |

回测覆盖的表：
- `cn_stock_indicators_buy`（指标买入）
- `cn_stock_indicators_sell`（指标卖出）
- 10 张策略表（`cn_stock_strategy_*`）

### 第7步 — basic_data_after_close_daily_job

| 顺序 | 函数 | 写入表 | 说明 |
|------|------|--------|------|
| 1 | `save_after_close_stock_blocktrade_data` | `cn_stock_blocktrade` | 大宗交易 |
| 2 | `save_after_close_stock_chip_race_end_data` | `cn_stock_chip_race_end` | 尾盘抢筹 |

> 注：这两个数据仅在收盘后才能获取，因此放在流水线最后。

---

## 四、月度维护任务 — `run_monthly`

**触发方式**：`cron.monthly` → shell 脚本
**触发时间**：每周三、周六 10:30
**用途**：清除 K 线历史缓存目录 `instock/cache/hist/*`，释放磁盘空间

---

## 五、日期选择机制

核心函数 `trade_time.get_trade_date_last()` 返回两个日期：

| 场景 | `run_date`（已收盘日） | `run_date_nph`（含盘中日） |
|------|----------------------|--------------------------|
| 交易日，已收盘（>=15:00） | 今天 | 今天 |
| 交易日，已开盘未收盘（9:30~15:00） | 上个交易日 | 今天 |
| 交易日，未开盘（<9:30） | 上个交易日 | 上个交易日 |
| 非交易日（周末/节假日） | 上个交易日 | 上个交易日 |

`run_template.run_with_args()` 根据**函数名前缀**决定使用哪个日期和参数：

| 函数名前缀 | 调用方式 | 使用日期 | 说明 |
|-----------|---------|---------|------|
| `save_nph_*` | `run_fun(run_date_nph, False)` | `run_date_nph` | 盘中可用数据，`before=False` 跳过守卫 |
| `save_after_close_*` | `run_fun(run_date, *args)` | `run_date` | 仅收盘后可用数据，始终用已收盘日 |
| 其他（无前缀） | `run_fun(run_date_nph, *args)` | `run_date_nph` | 通用处理函数 |

---

## 六、手动运行方式

```bash
# 运行完整流水线
./run_local_job.sh

# 运行单个任务
./run_local_job.sh basic_data_daily_job
./run_local_job.sh indicators_data_daily_job
./run_local_job.sh klinepattern_data_daily_job
./run_local_job.sh strategy_data_daily_job
./run_local_job.sh selection_data_daily_job
./run_local_job.sh basic_data_other_daily_job
./run_local_job.sh basic_data_after_close_daily_job
./run_local_job.sh backtest_data_daily_job

# 指定日期运行
./run_local_job.sh strategy_data_daily_job 2026-03-20
./run_local_job.sh strategy_data_daily_job 2026-03-01 2026-03-20  # 区间
./run_local_job.sh strategy_data_daily_job 2026-03-01,2026-03-05  # 多日
```

---

## 七、数据依赖关系

```
cn_stock_spot (实时行情)
  │
  ├──> cn_stock_selection (综合选股，独立数据源)
  │
  ├──> cn_stock_spot_buy (基本面选股，从 cn_stock_spot 筛选)
  │
  ├──> stock_hist_data 单例 (历史K线，被以下3个任务共享)
  │      │
  │      ├──> cn_stock_indicators ──> cn_stock_indicators_buy / _sell
  │      │
  │      ├──> cn_stock_pattern
  │      │
  │      └──> cn_stock_strategy_* (10张表)
  │
  └──> backtest_data_daily_job (依赖 indicators_buy/sell + strategy_* 表)
         回填 N 日收益率到上述表中
```

关键点：`stock_hist_data` 是**单例模式**（`singleton_type`），在同一进程中只初始化一次。indicators、klinepattern、strategy 三个并行任务共享同一份历史 K 线数据，避免重复拉取。
