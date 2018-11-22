from rqalpha.api import *



def init(context):
    # 这里选了000001.SZ作为参考基准，大家可以根据自己的不同需要进行修改；
    context.set_benchmark("000001.SZ")

    # 制定了一个买股的集合单子；存放在buyList里面的就是我们选出来后的要买的股
    context.buyList = []

    # curPflInfo 的key为当前持仓股票，value为股票信息
    # 如 context.curPflInfo = {'000001.XSHE':{'time':1,'avgCost':9.5}}
    context.curPflInfo = {}

    # avgCost是平均成本
    context.avgCost = 0

    # 持仓数
    context.holdSize = 10

    # 新买个股的初始仓位 每天开盘前初始化
    context.weight = 0

    # 止盈，可以是值，也可以是百分比制；
    context.stpPftPrice = 0.05

    # 止损，和止盈同样的道理
    context.stpLosRate = -0.05

    # 下单集合
    context.orderList = []



def handle_bar(context, bar_dict):
    pass


def handle_tick(context, tick):
    pass



def before_trading(context):
    """
    q = query(
        fundamentals.equity_valuation_indicator.market_cap
    ).filter(
        fundamentals.equity_valuation_indicator.market_cap<1e11
    ).order_by(
        fundamentals.equity_valuation_indicator.market_cap.asc()
    ).limit(10)
    df = get_fundamentals(q)
    context.allStocks = df.columns.values

    for stk in context.curPflInfo.keys():
        context.curPflInfo[stk]['holdDays'] += 1
    上面这个很基础的，通过市值来选取股，帮助文档里面能找到相关说明，这里就不多废话了,asc是从小到大取，
    如果选得多，成交机制也是从小到大进行成交;limit()为限制数量;
    接下来是过滤st和停牌，涨跌停股，目前不设置也不会买
    """
    pass


def after_trading(context):
    pass


# 过滤st和停牌股票
def filterStAndPaused(stkList,data_dict):
    stkList = [stk for stk in stkList if not is_st(stk) and data_dict[stk].sf == 0]
    return stkList


#过滤涨跌停股票
def filterLimitStk(stk,data_dict,context):
    price = history_bars(stk, 2, '1d', 'close')
    yesterday = price[-1]

    zt = round(1.10 * yesterday,2)
    dt = round(0.97 * yesterday,2)
    if dt < data_dict[stk].last < zt :
        return True
    else:
        return False





