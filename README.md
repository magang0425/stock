# InStock - A 股量化分析系统

InStock 是一套面向中国 A 股市场的量化数据采集、技术分析与策略筛选系统。自动化采集沪深 A 股行情数据，计算 30+ 种技术指标，识别 61 种 K 线形态，运行 10 种选股策略，并提供 Web 可视化界面进行数据浏览与个股分析。

## 功能概览

- **实时行情采集** — 自动抓取 4500+ 只 A 股及 ETF 的实时行情
- **技术指标计算** — MACD / KDJ / RSI / BOLL / ATR / DMI 等 30+ 种指标
- **K 线形态识别** — 基于 TA-Lib 的 61 种经典 K 线形态识别
- **量化选股策略** — 10 种内置策略（放量上涨、均线多头、海龟交易等）
- **策略回测** — 自动计算策略命中后 1/2/3/5/10/20/30/60 日收益率
- **数据看板** — 龙虎榜、资金流向、大宗交易、基本面选股等
- **Web 可视化** — Tornado Web 服务，K 线图表、指标图表交互浏览

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| 包管理 | uv |
| 技术分析 | TA-Lib |
| 数据处理 | pandas / numpy |
| 数据库 | MySQL 8.0（utf8mb4） |
| ORM | SQLAlchemy + PyMySQL |
| Web 框架 | Tornado |
| 部署 | Docker + Supervisor + Cron |

## 项目结构

```
instock/
├── cli.py                    # 命令行入口（instock-job / instock-web）
├── job/                      # 定时任务
│   ├── execute_daily_job.py  # 每日主任务（编排所有子任务）
│   ├── init_job.py           # 数据库初始化
│   ├── basic_data_daily_job.py           # 实时行情采集
│   ├── selection_data_daily_job.py       # 综合选股数据
│   ├── basic_data_other_daily_job.py     # 龙虎榜/资金流向/分红等
│   ├── indicators_data_daily_job.py      # 技术指标计算
│   ├── klinepattern_data_daily_job.py    # K线形态识别
│   ├── strategy_data_daily_job.py        # 选股策略执行
│   ├── backtest_data_daily_job.py        # 策略回测
│   └── basic_data_after_close_daily_job.py  # 收盘后数据（大宗交易等）
├── core/
│   ├── crawling/             # 数据爬取模块
│   │   ├── stock_hist_em.py  # 历史K线（东方财富 + 腾讯）
│   │   ├── stock_selection.py        # 选股器
│   │   ├── stock_lhb_em.py           # 龙虎榜（东方财富）
│   │   ├── stock_lhb_sina.py         # 龙虎榜（新浪）
│   │   ├── stock_fund_em.py          # 资金流向
│   │   ├── stock_dzjy_em.py          # 大宗交易
│   │   ├── stock_chip_race.py        # 抢筹数据
│   │   └── ...
│   ├── indicator/
│   │   └── calculate_indicator.py    # 技术指标计算引擎
│   ├── strategy/             # 选股策略
│   │   ├── enter.py          # 放量上涨
│   │   ├── keep_increasing.py        # 均线多头
│   │   ├── turtle_trade.py           # 海龟交易法则
│   │   ├── parking_apron.py          # 停机坪
│   │   ├── backtrace_ma250.py        # 回踩年线
│   │   ├── breakthrough_platform.py  # 突破平台
│   │   ├── low_backtrace_increase.py # 无大幅回撤
│   │   ├── high_tight_flag.py        # 高而窄的旗形
│   │   ├── climax_limitdown.py       # 放量跌停
│   │   └── low_atr.py               # 低ATR成长
│   ├── pattern/
│   │   └── pattern_recognitions.py   # K线形态识别引擎
│   ├── kline/
│   │   └── visualization.py          # K线可视化
│   ├── backtest/
│   │   └── rate_stats.py             # 回测收益率计算
│   ├── stockfetch.py         # 数据获取统一入口
│   ├── tablestructure.py     # 全部表结构定义
│   ├── singleton_stock.py    # 股票数据单例（缓存）
│   └── eastmoney_fetcher.py  # 东方财富请求封装
├── web/
│   ├── web_service.py        # Tornado Web 服务（端口 9988）
│   ├── dataTableHandler.py   # 数据表格 API
│   ├── dataIndicatorsHandler.py  # 指标图表 API
│   ├── templates/            # HTML 模板
│   └── static/               # 静态资源（CSS/JS/图片）
├── lib/
│   ├── database.py           # 数据库连接管理
│   ├── run_template.py       # 任务调度模板（日期路由）
│   ├── trade_time.py         # 交易时间判断
│   ├── singleton_type.py     # 单例元类
│   └── torndb.py             # Tornado 数据库适配
├── cache/hist/               # 历史K线本地缓存（gzip pickle）
└── log/                      # 运行日志
```

## 快速开始

### 环境要求

- Python 3.11
- MySQL 8.0+
- [uv](https://docs.astral.sh/uv/) 包管理器
- [TA-Lib](https://ta-lib.org/) C 库

### 本地运行

1. **安装依赖**

```bash
uv sync --frozen
```

2. **配置数据库连接**

创建 `.env` 文件：

```env
db_host=127.0.0.1
db_user=root
db_password=your_password
db_database=instockdb
db_port=3306
```

3. **运行数据采集任务**

```bash
# 运行完整流水线（首次运行会自动创建数据库和表）
./run_local_job.sh

# 运行单个任务
./run_local_job.sh basic_data_daily_job
./run_local_job.sh strategy_data_daily_job

# 指定日期
./run_local_job.sh strategy_data_daily_job 2026-03-20

# 日期区间
./run_local_job.sh strategy_data_daily_job 2026-03-01 2026-03-20

# 多个日期
./run_local_job.sh strategy_data_daily_job 2026-03-01,2026-03-05
```

4. **启动 Web 服务**

```bash
./run_local_web.sh
# 访问 http://localhost:9988
```

### Docker 部署

```bash
cd docker
docker-compose up -d
```

Docker 环境下定时任务通过 cron 自动调度，无需手动运行。

## 定时任务

详细的任务调度文档参见 [cron.md](cron.md)。

### 调度概览

| 任务 | 周期 | 时间 | 说明 |
|------|------|------|------|
| 盘中刷新 | 每 30 分钟 | 交易日 9:00~15:30 | 刷新实时行情 |
| 收盘后主任务 | 每工作日 | 17:30 | 完整数据流水线 |
| 月度维护 | 周三/周六 | 10:30 | 清除历史缓存 |

### 收盘后流水线

```
init_job           → 检查/创建数据库
    ↓
basic_data_daily   → 实时行情采集
    ↓
selection_data     → 综合选股
    ↓
┌─────────────────────── 并行 ───────────────────────┐
│  basic_data_other  → 龙虎榜/资金流向/分红/涨停原因  │
│  indicators_data   → 技术指标计算                    │
│  klinepattern_data → K线形态识别                     │
│  strategy_data     → 10种选股策略                    │
└────────────────────────────────────────────────────┘
    ↓
backtest_data      → 策略回测（补充N日收益率）
    ↓
after_close_data   → 大宗交易 / 尾盘抢筹
```

## 技术指标

系统基于 TA-Lib 计算以下技术指标，存入 `cn_stock_indicators` 表：

| 类别 | 指标 |
|------|------|
| 趋势 | MACD、TRIX、DMA、DMI（PDI/MDI/ADX/ADXR）、Supertrend、DPO |
| 动量 | KDJ、RSI（6/12/14/24）、CCI（14/84）、ROC、WR（6/10/14）、MFI、StochRSI、PPO |
| 波动 | BOLL（布林带）、ATR、VHF、ENE |
| 成交量 | OBV、VR、VWMA、VOL MA（5/10）、EMV |
| 情绪 | PSY（心理线）、BRAR（人气意愿）、CR（能量指标）、RVI |
| 均线 | MA（6/10/12/20/24/50/200）、TEMA |
| 其他 | BIAS（乖离率）、FI（力量指标）、SAR、WT（Wave Trend） |

### 指标信号筛选

- **买入信号**（`cn_stock_indicators_buy`）：KDJ K>=80, D>=70, J>=100, RSI6>=80, CCI>=100, CR>=300, WR6>=-20, VR>=160
- **卖出信号**（`cn_stock_indicators_sell`）：KDJ K<20, D<30, J<10, RSI6<20, CCI<-100, CR<40, WR6<=-80, VR<40

## K 线形态

基于 TA-Lib CDL 系列函数识别 61 种 K 线形态，存入 `cn_stock_pattern` 表：

两只乌鸦、向上跳空的两只乌鸦、三只乌鸦、三胞胎乌鸦、三线打击、乌云压顶、十字暮星、十字星、上吊线、陷阱、修正陷阱、颈内线、颈上线、插入、射击之星、停顿形态、大敌当前、风高浪大线、吞噬模式、弃婴、收盘缺影线、十字、向上/下跳空并列阳线、长脚十字、黄包车夫、光头光脚/缺影线、三内部上涨和下跌、三外部上涨和下跌、南方三星、三个白兵、捉腰带线、脱离、藏婴吞没、反击线、蜻蜓十字/T形十字、暮星、墓碑十字/倒T十字、锤头、母子线、十字孕线、家鸽、倒锤头、反冲形态、由较长缺影线决定的反冲形态、梯底、长蜡烛、相同低价、铺垫、十字晨星、晨星、刺透形态、上升/下降三法、分离线、短蜡烛、纺锤、条形三明治、探水竿、跳空并列阴阳线、三星、奇特三河床、上升/下降跳空三法

## 选股策略

10 种内置选股策略，每日自动筛选符合条件的股票：

### 放量上涨（enter）

筛选当日放量大涨的股票。

- 当日涨幅 >= 2% 且收盘价 > 开盘价
- 当日成交额 >= 2 亿
- 当日成交量 / 5 日平均成交量 >= 2

### 均线多头（keep_increasing）

筛选 MA30 持续上升的趋势股。

- 30 日前的 MA30 < 20 日前的 MA30 < 10 日前的 MA30 < 当日 MA30
- 当日 MA30 / 30 日前 MA30 > 1.2

### 停机坪（parking_apron）

筛选涨停后高位横盘整理的股票。

- 最近 15 日内有单日涨幅 > 9.5% 的放量上涨
- 涨停后 1 日：高开，收盘上涨，收盘与开盘差 < 3%
- 涨停后 2~3 日：高开，收盘上涨，收盘与开盘差 < 3%，日涨跌幅在 5% 以内

### 回踩年线（backtrace_ma250）

筛选突破年线后回踩确认的股票。

- 前段从 MA250 以下向上突破
- 后段在 MA250 以上运行
- 最高价日与最低价日相差 10~50 日
- 回踩伴随缩量：最高日量 / 最低日量 > 2，最低价 / 最高价 < 0.8

### 突破平台（breakthrough_platform）

筛选突破 MA60 平台的股票。

- 60 日内某日收盘价 >= MA60 > 开盘价（从下向上穿越）
- 突破当日满足「放量上涨」条件
- 突破前收盘价与 MA60 偏离在 -5%~20% 之间

### 海龟交易法则（turtle_trade）

经典趋势跟踪策略。

- 当日收盘价 >= 最近 60 日最高收盘价（创新高入场）

### 无大幅回撤（low_backtrace_increase）

筛选稳健上涨、没有大幅回调的股票。

- 60 日涨幅 >= 60%
- 期间无单日跌幅 > 7%、无高开低走 > 7%
- 无连续两日累计跌幅 > 10%

### 高而窄的旗形（high_tight_flag）

筛选快速拉升后窄幅整理的强势股。

- 龙虎榜上有机构参与
- 当日收盘价 / 前 10~24 日最低价 >= 1.9
- 期间有连续两日涨幅 >= 9.5%

### 放量跌停（climax_limitdown）

筛选放量跌停的异动股（可能的恐慌性抛售）。

- 当日跌幅 > 9.5%
- 成交额 >= 2 亿
- 成交量 / 5 日平均成交量 >= 4

### 低 ATR 成长（low_atr）

筛选低波动高弹性的股票。

- 至少上市交易 250 日
- 最近 10 日 ATR < 10
- 最近 10 日最高收盘价 / 最低收盘价 > 1.1

## 数据库表

系统共 29 张表，分为以下几类：

### 行情数据

| 表名 | 说明 |
|------|------|
| `cn_stock_spot` | A 股实时行情 |
| `cn_etf_spot` | ETF 实时行情 |
| `cn_stock_selection` | 综合选股数据 |

### 技术分析

| 表名 | 说明 |
|------|------|
| `cn_stock_indicators` | 技术指标 |
| `cn_stock_indicators_buy` | 指标买入信号 |
| `cn_stock_indicators_sell` | 指标卖出信号 |
| `cn_stock_pattern` | K 线形态 |

### 选股策略

| 表名 | 说明 |
|------|------|
| `cn_stock_strategy_enter` | 放量上涨 |
| `cn_stock_strategy_keep_increasing` | 均线多头 |
| `cn_stock_strategy_parking_apron` | 停机坪 |
| `cn_stock_strategy_backtrace_ma250` | 回踩年线 |
| `cn_stock_strategy_breakthrough_platform` | 突破平台 |
| `cn_stock_strategy_low_backtrace_increase` | 无大幅回撤 |
| `cn_stock_strategy_turtle_trade` | 海龟交易 |
| `cn_stock_strategy_high_tight_flag` | 高而窄旗形 |
| `cn_stock_strategy_climax_limitdown` | 放量跌停 |
| `cn_stock_strategy_low_atr` | 低 ATR 成长 |

### 市场数据

| 表名 | 说明 |
|------|------|
| `cn_stock_lhb` | 龙虎榜（东方财富） |
| `cn_stock_top` | 龙虎榜（新浪） |
| `cn_stock_blocktrade` | 大宗交易 |
| `cn_stock_fund_flow` | 个股资金流向 |
| `cn_stock_fund_flow_industry` | 行业资金流向 |
| `cn_stock_fund_flow_concept` | 概念资金流向 |
| `cn_stock_chip_race_open` | 早盘抢筹 |
| `cn_stock_chip_race_end` | 尾盘抢筹 |
| `cn_stock_bonus` | 分红配送 |
| `cn_stock_limitup_reason` | 涨停原因 |
| `cn_stock_spot_buy` | 基本面选股 |
| `cn_stock_attention` | 用户关注 |

## 数据来源

| 来源 | 数据 |
|------|------|
| 东方财富 | 实时行情、历史K线、龙虎榜、资金流向、大宗交易、选股器 |
| 腾讯财经 | 日线行情（东方财富降级备用） |
| 新浪财经 | 龙虎榜统计 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `db_host` | 数据库主机 | `localhost` |
| `db_user` | 数据库用户 | `root` |
| `db_password` | 数据库密码 | `root` |
| `db_database` | 数据库名称 | `instockdb` |
| `db_port` | 数据库端口 | `3306` |

## License

MIT
