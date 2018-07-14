# -*- coding:utf-8 -*-

from douyin import util 
from douyin import dbutil as db
from os import path
import sys

global _browser_
global _config_
global _result_
global _base_path_
global _c_ # 数据库连接
global _d_pool_ # 已经下载了的视频的id池
global _debug_ 



def __run__():
    util._get_basic_info(_browser_,_config_,_result_)
    _p_len = 0
    _l_len = 0
    if _config_['dpv']: _p_len = util._get_post_request_data(_browser_,_config_,_result_)
    if _config_['dlv']: _l_len = util._get_like_request_data(_browser_,_config_,_result_)
    _browser_.quit()
    print('浏览器退出成功...')
    print('数据采集完毕,发表的视频[' + str(_p_len) + ']条,喜欢的视频[' + str(_l_len) + ']条!')
    return util._download_video(_config_,_result_,_d_pool_,_c_)


if __name__ == '__main__':
    print('>>> 脚本初始化中... ...')
    _base_path_ = path.dirname(path.realpath(__file__))
    _config_ = util._read_config(_base_path_ + '/config.txt',_base_path_,sys.argv)
    print('读取配置文件完毕...')
    _debug_ = util._debug_ = db._debug_ = _config_['debug']
    _c_ = db.get_conn(_base_path_+'/douyin/douyin.db')
    print('数据库连接创建完毕!')
    _d_pool_ = db.ini_d_pool(_c_,_config_)
    print('初始化已下载池完毕!')
    _browser_ = util._init_browser({
       'driver_path':path.dirname(path.realpath(__file__))+'/lib/chromedriver.exe'
    },_config_['headless'])
    print('初始化浏览器成功...')
    _result_ = {}
    print('>>> Donyin下载任务开始... ...')
    r = __run__()
    print('Donyin下载任务结束... ...')
    print('视频下载完毕,发表的视频[' + str(r['l_len'] - 1) + ']条,喜欢的视频[' + str(r['p_len'] - 1) + ']条!')

    