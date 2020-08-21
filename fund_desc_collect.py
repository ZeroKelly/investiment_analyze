import os
import re
import json
import pandas as pd
import requests


def compose_header(header_str):
    headers = dict()
    for i in re.findall('(.*?): (.*)', header_str):
        headers[i[0]]=i[1]
    return headers

def init_fake_session():
    '''
    @return session: with fake request header
    '''
    header_str = '''Accept: */*
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7
Connection: keep-alive
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15
Host: fund.eastmoney.com
Referer: http://fund.eastmoney.com/daogou/aleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'''

    headers = compose_header(header_str)
    session = requests.Session()
    for key in session.headers.keys():
        session.headers[key] = headers[key]
    return session

def get_data(session):
    '''connect to eastmoney and collect all basic fund information
    @param session: session to use
    @return: unformalized data
    '''
    url_idx = 'http://fund.eastmoney.com/daogou/'
    main_page = session.get(url_idx)
    fund_count = re.findall('共找到 <span id="fund_count">(.*?)</span>只基金符合您的要求', main_page.content.decode('utf-8'))[0]
    url_data = 'http://fund.eastmoney.com/data/FundGuideapi.aspx?dt=0&sd=&ed=&sc=3y&st=desc&pi=1&pn=%s&zf=diy&sh=list'%(fund_count)
    data = session.get(url_data)
    return data

def formalize_data(data):
    '''
    @param data: unformalized data collected by get_data()
    @return: pandas_df
    '''
    data = data.content.decode('utf-8').replace('var rankData =', '')
    json.loads(data).keys()
    data = json.loads(data).get('datas')
    data = [i.split(',') for i in data]
    data = pd.DataFrame(data)
    heads = ['基金代码', '基金名称', '名称缩写', '基金类型', '今年来', '近1周', '近1月','近3月', '近6月', '近1年','近2年', '近3年','n0', '不知道是啥', 'page_num', '数据来源日期','净值','日增长率', 'total_page_num','手续费', '购买起点（元)', 'page_num2', '原先手续费', '现在手续费']
    data.columns = heads
    return data

def collect_index_info():
    '''
    return: pandas_df about basic information of fund collected from eastmoney
    '''
    session = init_fake_session()
    data = get_data(session)
    data = formalize_data(data)
    return data

if __name__ == '__main__':
    data = collect_index_info()
    if not os.path.exists('./data'):
        os.mkdir('./data')
    data.to_csv('./data/基金基本数据抓取.csv', index=False)
