
"""
彼得里奇 PEG估值法

策略：计算每只股票的PEG值，并排序，取PEG值最小的前n支股票，作为待买股票即可！

概念：
    EPS(Earning Per share) 标示每股收益
    PE(Price to Earning Ration) 标示市盈率，是当前股价（P）相对每股收益（EPS）的比值：

    “滚动市盈率”（又称市盈率TTM),
    “静态市盈率”（又称市盈率LYR）
    “动态市盈率”

    G（Growth Rate of Expected Profit）表示企业的收益增长率。收益增长率的计算方法不一，简便起见，本文取EPS增长率：

    PEG= PE/(G∗100)

    从以上公式可以看出，PE蕴含着股价的信息，PEG是一个股价相对于收益增长率的比值。
    直观来讲，PEG越高，代表该公司的股价有被高估的可能性，不建议买。
    反之，PEG越低，代表该公司的股价有被低估的可能性，考虑买入(*一般情况下，PEG越低越好)。
"""
# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。
import time


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    # context.shall_trade = False

    # 每天满足PEG值 < 0.5 可以买入的股票列表
    context.buy_stock_list = []

    # 每天需要清仓的股票列表
    context.sell_stock_list = []

    # 每周一先卖掉调出的股票
    scheduler.run_weekly(schedule_clear, weekday=1)

    # 每周二买入新调入的股票
    scheduler.run_weekly(schedule_buy, weekday=2)


# before_trading此函数会在每天交易开始前被调用，当天只会被调用一次
def before_trading(context):
    pass


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    pass


def schedule_clear(context, bar_dict):
    # 待买列表
    context.buy_stock_list = buy_stocks_list(context)
    # 待卖列表
    context.sell_stock_list = sell_stocks_list(context, context.buy_stock_list)

    basket_sell(context.sell_stock_list)


def schedule_buy(context, bar_dict):
    basket_buy(context.buy_stock_list)
    logger.info("最新买入的股票是：" + str(context.buy_stock_list))


def get_PEG(context):
    # 选取csi300的股票作为股票池
    # csi300_stocks_list = index_components('000300.XSHG')

    csi300_stocks_list = index_components('000001.XSHG')

    # query_PEG = query(fundamentals.eod_derivative_indicator.pe_ratio, fundamentals.financial_indicator.inc_adjusted_net_profit)
    #    .filter(fundamentals.eod_derivative_indicator.stockcode.in_(csi300_stocks_list))\
    #    .filter(fundamentals.financial_indicator.inc_adjusted_net_profit > 0)\
    #    .filter(fundamentals.eod_derivative_indicator.pe_ratio > 0)

    # 查询全市场股票的市盈率和净利润 - 扣除非经常损益，并且剔除掉小于0的情况，来规避负增长和负PE的公司
    query_PEG = query(fundamentals.eod_derivative_indicator.pe_ratio,
                      fundamentals.financial_indicator.inc_adjusted_net_profit) \
        .filter(fundamentals.eod_derivative_indicator.stockcode.in_(csi300_stocks_list))\
        .filter(fundamentals.financial_indicator.inc_adjusted_net_profit > 0) \
        .filter(fundamentals.eod_derivative_indicator.pe_ratio > 0)

    # 得到一个有pe_ratio和inc_adjusted_net_profit的dataframe
    df_PE_G = get_fundamentals(query_PEG)

    # 去除PE或inc_adjusted_net_profit为非数字的股票所在行
    df_PE_G.dropna()

    # 拿到股票的pe_ratio的 Series
    series_PE = df_PE_G.ix['pe_ratio']

    # 拿到股票的inc_adjusted_net_profit的Series
    series_G = df_PE_G.ix['inc_adjusted_net_profit']

    # 将两个Series相除，拿到PEG值
    series_PEG = series_PE / series_G
    # 对返回的PEG Series做升序排列
    series_PEG.sort(ascending=True)

    # 只拿PEG值排前10个的股票：
    return series_PEG[0:10]


# 获得买入股票的列表，通过PEG评估进行筛选
def buy_stocks_list(context):
    list_to_buy = []

    # 拿到计算好的PEG值的Series，其中index是股票代码，数值为PEG
    series_PEG = get_PEG(context)
    series_PEG.index.tolist()

    # 我们选取PEG值小于0.5的低估值股票列表
    temp_PEG_list = series_PEG[series_PEG < 0.5].index.tolist()

    # 过滤掉停牌的股票
    for stock in temp_PEG_list:
    #for stock in series_PEG.index.tolist():
        if not is_suspended(stock):
            list_to_buy.append(stock)
        # else:
        # logger.info('tingpai: ' + stock)

    # logger.info("打算调仓到：" + str(len(list_to_buy)) + " 个股票的仓位， 满足< 0.5PEG值并且非停牌")
    return list_to_buy


# 获得卖出信号
# 输入：context（全局变量），list_to_buy为list类型，表示待买入的股票
# 输出：list_to_sell为list类型，表示不在将要买入的股票列表，却又在仓位中的股票
def sell_stocks_list(context, list_to_buy):
    list_to_sell = []
    for stock_sell in context.portfolio.positions:
        # 该处于已有持仓的股票并不在新的符合买入标准的股票列表中，或者已经停牌了无法卖出
        if stock_sell not in list_to_buy and not is_suspended(stock_sell):
            list_to_sell.append(stock_sell)
    # logger.info("需要卖出的股票列表：" + str(list_to_sell))
    return list_to_sell


# 买入操作
def basket_buy(list_to_buy):
    # 计算每个股票的买入比例
    if len(list_to_buy) > 0:
        weight = 1 / len(list_to_buy)
        for stock in list_to_buy:
            # 买入该符合条件的股票
            order_target_percent(stock, weight)

# 卖出操作
def basket_sell(list_to_sell):
    for stock_sell in list_to_sell:
        order_target_value(stock_sell, 0)



