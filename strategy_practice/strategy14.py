

"""
RPS波动率差价择时

https://www.joinquant.com/post/12453
"""


def initialize(context):
    # 设置选用指数、设置基准、设置交易费率
    g.stocksIndex = '399300.XSHE'
    set_benchmark(g.stocksIndex)
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003,
                             close_today_commission=0, min_commission=5), type='stock')
    set_slippage(FixedSlippage(0.02))

    # 获取所有价格
    df_index = get_price(g.stocksIndex, start_date='2005-05-01', end_date='2018-4-30', frequency='daily',
                         fields=['close', 'open', 'high', 'low'], skip_paused=False, fq='pre')
    # 上、下波动率：以开盘价为基准，开盘价以上的波动定义为上行波动率，反之为下行波动率。
    df_index['uvolatility'] = (df_index.high - df_index.open) / df_index.open
    df_index['dvolatility'] = (df_index.open - df_index.low) / df_index.open
    # 剪刀差
    df_index['u_d'] = df_index['uvolatility'] - df_index['dvolatility']

    # 剪刀差的移动平均数
    df_index['u_d_MA10'] = pd.rolling_mean(df_index.u_d, window=10, min_periods=10)
    df_index['u_d_MA20'] = pd.rolling_mean(df_index.u_d, window=20, min_periods=20)
    df_index['u_d_MA30'] = pd.rolling_mean(df_index.u_d, window=30, min_periods=30)
    df_index['u_d_MA40'] = pd.rolling_mean(df_index.u_d, window=40, min_periods=40)
    df_index['u_d_MA50'] = pd.rolling_mean(df_index.u_d, window=50, min_periods=50)
    df_index['u_d_MA60'] = pd.rolling_mean(df_index.u_d, window=60, min_periods=60)
    df_index['u_d_MA70'] = pd.rolling_mean(df_index.u_d, window=70, min_periods=70)
    df_index['u_d_MA80'] = pd.rolling_mean(df_index.u_d, window=80, min_periods=80)
    df_index['u_d_MA90'] = pd.rolling_mean(df_index.u_d, window=90, min_periods=90)
    df_index['u_d_MA100'] = pd.rolling_mean(df_index.u_d, window=100, min_periods=100)

    '''----------------------------------强弱RPS值-------------------------------------'''
    '''
    1、 计算RPS值: RPS_1=(当前涨跌幅-MIN(250交易日涨幅))/(MAX(250交易日涨幅)-MIN(250交易日涨幅)) （注：其值在0%到100%区间内） 
        注：原文如此，个人认为应当修正为：RPS_1=(当日收盘价-250交易日最低价)/(250交易日最高价-250交易日最低价) （注：其值在0%到100%区间内） 
    2、 然后取10个交易日移动平均值：RPS=MA(RPS_1)
    '''
    df_index['MIN_250'] = pd.rolling_min(df_index.close, window=250, min_periods=100)
    df_index['MAX_250'] = pd.rolling_max(df_index.close, window=250, min_periods=100)
    df_index['RPS_1'] = (df_index['close'] - df_index['MIN_250']) / (df_index['MAX_250'] - df_index['MIN_250'])
    df_index['RPS_MA10'] = pd.rolling_mean(df_index.RPS_1, window=10, min_periods=10)
    df_index.index = df_index.index.date
    g.df_index = df_index


'''----------------------------------回测函数-------------------------------------'''


def handle_data(context, data):
    # 取前一日RPS值
    rps = g.df_index.at[context.previous_date, 'RPS_MA10']
    # 采用原文的60日移动平均线
    len_str = 'u_d_MA60'
    '''
    #这部分是分档，效果很一般，不知道原文如何达到那么好的效果
    len_str='u_d_MA20'
    if rps>0.2:
        len_str='u_d_MA40'

    if rps>0.4:
        len_str='u_d_MA60'
    if rps>0.6:
        len_str='u_d_MA80'  
    if rps>0.8:
        len_str='u_d_MA100' 
    '''
    # 交易函数，如果前一天的剪刀差移动平均大于0，就交易，否则清仓
    if g.df_index.at[context.previous_date, len_str] > 0:
        if (len(context.portfolio.positions) == 0):
            order_value(g.stocksIndex, context.portfolio.cash)
    else:
        if (len(context.portfolio.positions) > 0):
            order_target_value(g.stocksIndex, 0)
