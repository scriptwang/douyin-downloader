# -*- coding:utf-8 -*-
import sqlite3 as db
import os

global _debug_


def get_conn(db_file,check_same_thread=False):
    # 如果文件夹不存在则首先创建文件夹
    if not os.path.exists(os.path.dirname(db_file)):
        os.makedirs(os.path.dirname(db_file)) #先创建文件夹
    return db.connect(db_file,check_same_thread=check_same_thread)

def exe_qry(conn,sql):
    if _debug_ : print(' ------->> exe_qry:' + sql)
    cursor = conn.execute(sql)
    rs = cursor.fetchall()
    return rs

#insert update delete 
def exe_dml(conn,sql):
    if _debug_ : print(' ------->> exe_dml:' + sql)
    conn.execute(sql)
    conn.commit()


def ini_d_pool(conn,_config_):
    r = {}
    rs = exe_qry(conn,"select aweme_id,video_type from douyin where douyin_id = '%s'" % (_config_['user_id']))
    for i in rs:r[i[0]] = i[1]
    sql = '''
        select  'post' as nm,case when max(video_count) is null then 1 else max(video_count) + 1 end as cnt,
        case when max(download_time) is null then '还没下载过此小姐姐/小哥哥发表的视频呢><' else max(download_time) end as time
        from douyin where douyin_id = '%s' AND video_type = 'post'
        union all
        select  'like' as nm,case when max(video_count) is null then 1 else max(video_count) + 1 end as cnt,
        case when max(download_time) is null then '还没下载过此小姐姐/小哥哥喜欢的视频呢><' else max(download_time) end as time
        from douyin where douyin_id = '%s' AND video_type = 'like';
    ''' % (_config_['user_id'],_config_['user_id'])
    rs = exe_qry(conn,sql)
    for i in rs:
        print ('记录上一次下载计数/时间:' + str(i[0]) + ' 最后下载计数:' + str(i[1] - 1) + ' 最后下载时间:' + str(i[2]))
        r[i[0]] = i[1]
    return r
