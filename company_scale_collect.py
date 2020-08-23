from fund_desc_collect import *
from bs4 import BeautifulSoup

def get_company_table():
    session = init_fake_session()
    url = 'http://fund.eastmoney.com/Company/default.html'
    company_page = session.get(url).content.decode('utf-8')
    soup = BeautifulSoup(company_page)
    tb = soup.find_all('table', attrs={'class':'ttjj-table ttjj-table-hover common-sort-table'})[0]
    company_table = parse_manager_info_table(tb)
    company_table.columns = ['序号', '基金公司', '相关链接', '成立时间', '天相评级', '全部管理规模(亿元)(统计时间)', '全部基金数',
       '全部经理数']
    return company_table

def company_scale_str_to_float(copany_scale_str):
    copany_scale_str = copany_scale_str.replace(',', '')
    scale_num = copany_scale_str.split('\xa0\xa0 ')[0]
    try:
        return float(scale_num)
    except:
        return None

if __name__ == '__main__':
    company_table = get_company_table()
    company_table['全部管理规模(亿元)'] = company_table['全部管理规模(亿元)(统计时间)'].apply(company_scale_str_to_float)
    company_table.to_csv('./data/公司规模评估.csv', index=False)