import pandas as pd
import requests
import re
import json
from bs4 import BeautifulSoup

from fund_desc_collect import *


def load_data():
    try:
        data = pd.read_csv('./data/基金基本数据抓取.csv')
    except:
        data = collect_index_info()
    return data

def code_validation(code):
    code = str(code)
    if len(code) < 6:
        code = (6-len(code))*'0'+code
    return code

def get_fund_detail_page(session, code_num):
    valid_code = code_validation(code_num)
    url = 'http://fund.eastmoney.com/%s.html'%(valid_code)
    page = session.get(url)
    content = page.content.decode('utf-8')
    return content

def get_follow_error(content):
    follow_error = re.findall('跟踪误差：</a>(.*?)</td>', content)
    if len(follow_error) < 1:
        return None
    return follow_error[0]

def parse_fund_detail(content):
    fund_scale, manager_url, start_time = re.findall('基金规模</a>：(.*?)</td>.*基金经理：<a href="(.*?)">.*>成 立 日</span>：(.*?)<', content)[0]
    follow_error = get_follow_error(content)
    return [fund_scale, manager_url, start_time, follow_error]

def get_manager_info(session, manager_url):
    manager_page = session.get(manager_url)
    content = manager_page.content.decode('utf-8')
    manager_log, manager_profile = soup.find_all(name='table', attrs={'class':'w782 comm jloff'})
    return manager_log, manager_profile

def parse_manager_info_table(table):
    th = []
    tds = []
    count = 0
    for row in table.find_all('tr'): 
        if count < 1:
            th = [i.text for i in row.find_all('th')]
            count+=1
            continue
        tds.append([i.text for i in row.find_all('td')]) 
    res = pd.DataFrame(tds, columns=th)
    return res

def get_idx_fund_detail(idx_data):
    session = init_fake_session()
    count = 0
    total = idx_data.shape[0]
    fund_detail = []
    for code in idx_data['基金代码']:
        if count%100 == 0:
            print('%s/%s'%(count, total))
        count+=1
        detail_page = get_fund_detail_page(session, code)
        fund_detail.append([code]+parse_fund_detail(detail_page))
        time.sleep(0.01)
    fund_detail_df = pd.DataFrame(fund_detail, columns=['基金代码', '基金规模', '基金经理url', '成立时间', '跟踪误差率'])
    idx_fund_detail = pd.merge(idx_data, fund_detail_df, on='基金代码', how='left')
    return idx_fund_detail

if __name__ == '__main__':
    total_data = load_data()
    idx_data = total_data[total_data['基金类型'].str.find('指数')!=-1]
    idx_fund_detail = get_idx_fund_detail(idx_data)
    idx_fund_detail.to_csv('指数基金细节表.csv', index=False)