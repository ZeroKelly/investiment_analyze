from idx_fund_detail_collect import *
from fund_desc_collect import *
from datetime import datetime
import math

def percentage_str_to_float(s):
    try:
        return float(s.split('%')[0])
    except:
        return None

def rank_normalization(rank_str):
    try:
        rank, total = rank_str.split('|')
        return float(rank)/float(total)
    except:
        return None

def duration(start_time, end_time=None):
    '''
    @param time_str: 20xx-xx-xx format str
    @return: duration day int
    '''   
    start_time = datetime.strptime(start_time, '%Y-%m-%d')
    if end_time is None: 
        end_time = datetime.today()
    else:
        end_time = datetime.strptime(end_time, '%Y-%m-%d')
    duration = (end_time-start_time).days
    return duration

def manager_eval(session, manager_url, view_detail=False):
    '''
    @param session: session to get info
    @param manager_url: url to the manager profile page
    @param view_detail: display the manager profile table if set True
    '''
    manager_log, manager_profile = get_manager_info(session, manager_url)
    manager_log = parse_manager_info_table(manager_log)
    manager_profile = parse_manager_info_table(manager_profile)
    current_manager_condition = manager_log.iloc[0, :]
    current_manager_duration = duration(current_manager_condition['起始期'])
    rate_of_return = percentage_str_to_float(current_manager_condition['任职回报'])
    manager_work_duration_year = duration(manager_profile['起始时间'].iloc[-1])/365
    manager_profile['return_cmp2ave'] = manager_profile['任职回报'].apply(percentage_str_to_float) - manager_profile['同类平均'].apply(percentage_str_to_float)
    manager_profile['normalized_rank'] = manager_profile['同类排名'].apply(rank_normalization)
    mean_rank = manager_profile.normalized_rank.mean()
    mean_return_ratio = manager_profile.return_cmp2ave.mean()
    win_ratio = manager_profile[manager_profile.return_cmp2ave>0].shape[0]/manager_profile.shape[0]
    good_ratio = manager_profile[manager_profile.normalized_rank<0.5].shape[0]/manager_profile.shape[0]
    fund_num = manager_profile.shape[0]
    if view_detail:
        display(manager_log)
        display(manager_profile)
    return current_manager_duration, rate_of_return, manager_work_duration_year, fund_num, mean_rank, mean_return_ratio, win_ratio, good_ratio

def get_manager_eval_df(data):
    '''
    @param data: 基金细节表，含基金经理介绍页面链接
    @return: 基金经理评估统计量
    '''
    session = init_fake_session()
    manager_eval_info = []
    total = data.shape[0]
    count = 0
    for _, row in data[['基金代码', '基金经理url']].iterrows():
        if count % 50 == 0:
            print('%s/%s'%(count, total))
        code = row['基金代码']
        manager_url = row['基金经理url']
        try:
            manager_eval_info.append([code]+list(manager_eval(session, manager_url)))
        except:
            print(manager_url)
            break
        count += 1
    manager_eval_df = pd.DataFrame(manager_eval_info, columns=['基金代码', '当前经理管理天数', '当前回报率', '经理工作年限', '经理管理过的基金数量', '经理平均名次', '经理平均回报率', '跑赢均值比例', '排名在前50%比例'])
    return manager_eval_df

if __name__ == '__main__':
    data = pd.read_csv('./data/指数基金细节表.csv')
    manager_eval_df = get_manager_eval_df(data)
    data = pd.merge(data, manager_eval_df, on='基金代码', how='left')
    data.to_csv('./data/基金经理评估表.csv')
    print('基金经理评估完成')

