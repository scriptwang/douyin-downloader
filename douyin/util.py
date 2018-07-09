# -*- coding:utf-8 -*-

import time
import requests
import re
import random
import math
import datetime
import os
import configparser
import logging
from os import path
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.chrome.options import Options
from douyin.cons import *



def _read_config(config_path,_base_path_,args):
    def _get_user_id(user_id,args):
        if len(args) >= 2:
            print('从命令行读取抖音id[' + str(args[1]) + ']...')
            return args[1]
        else:
            print('从配置文件读取抖音id[' + str(user_id) + ']...')
            return  user_id
    config = configparser.ConfigParser()
    with open(config_path,'r',encoding='utf-8') as cfgfile:
        config.readfp(cfgfile)
        user_id = _get_user_id(str(config.get("base_config","user_id")),args)
        download_path = str(config.get("base_config","download_path"))
        if download_path == 'defalut':download_path = _base_path_
        timeout = float(config.get("base_config","timeout"))
        headless = config.get("base_config","headless")
        if headless == 'False':headless = False
        elif headless == 'True':headless = True
        slrv = config.get("base_config","single_like_requests_value")
        mipt = config.get("base_config","min_post_wait_time")
        mapt = config.get("base_config","max_post_wait_time")
        milt = config.get("base_config","min_like_wait_time")
        malt = config.get("base_config","max_like_wait_time")
        midt = config.get("base_config","min_down_wait_time")
        madt = config.get("base_config","max_down_wait_time")
        return {'user_id':user_id,'download_path':download_path,'timeout':timeout,'headless':headless,
        'slrv':slrv,'mipt':mipt,'mapt':mapt,'milt':milt,'malt':malt,'midt':midt,'madt':madt}

def _init_browser(args,headless = True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    if 'extension_path' in args:
        chrome_options.add_extension(args['extension_path'])
    LOGGER.setLevel(logging.WARNING)
    return webdriver.Chrome(executable_path=args['driver_path'],chrome_options=chrome_options)


# 拿到基本信息
def _get_basic_info(browser,_config_,_result_):
    share_link = 'https://www.douyin.com/share/user/'+_config_['user_id']+'?share_type=link'
    browser.get(share_link)
    time.sleep(float(_config_['timeout'])/2)
    title = browser.find_element_by_xpath('//body/div/div[1]/div[2]/div/p').text
    desc = None
    try:
        desc = browser.find_element_by_xpath('//body/div/div[1]/div[2]/div[2]/div/span').text
    except Exception as e:pass
    _result_['title'] = title
    print('获取小姐姐/小哥哥"'+title+'('+_config_['user_id']+')"基本信息成功!')
    if desc is not None:
        _result_['desc'] = title
        print(title + ':' + desc)


# 拿到发表的视频,因为抖音有请求限制,所以用hook ajax请求的方式拿到数据
def _get_post_request_data(browser,_config_,_result_):
    st = datetime.datetime.now()
    print('>>> 请求发表视频数据中(可能会比较慢).....')
    print('最小请求等待时间为:' + str(_config_['mipt']) +'s 最大请求等待时间为:' + str(_config_['mapt']) + 's')
    share_link = 'https://www.douyin.com/share/user/'+_config_['user_id']+'?share_type=link'
    browser.get(share_link)
    time.sleep(float(_config_['timeout'])/2)
    browser.execute_script(rigister_function)
    browser.execute_script(show_like)
    post_btn = browser.find_element_by_xpath('//body/div/div[1]/div[3]/div/div[1]')
    post_btn.click()
    # 滚动请求直到文档的底部
    is_bottom = False
    _len = 0
    while (not is_bottom):
        browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        t = random.randint(15,20)/10
        if t < float(_config_['mipt']):t = float(_config_['mipt'])
        if t > float(_config_['mapt']):t = float(_config_['mapt'])
        time.sleep(t)
        _len = int(browser.execute_script(' return window.resCnt()'))
        print(str(_len) + '条发表视频数据已添加!(随机等待请求时间:' + str(t) + 's)' )
        is_bottom = browser.execute_script(scroll_down)
    browser.execute_script(final_ajax)
    time.sleep(float(_config_['timeout'])/2)
    _result_['post'] = browser.execute_script(' return window.finalRes')
    _len = int(browser.execute_script(' return window.resCnt()'))
    print(str(_len) + '条发表视频数据已添加!(随机等待请求时间:' + str(t) + 's)' )
    et = datetime.datetime.now()
    print('请求用时:'+ str((et - st).seconds) + 's')
    return _len


# 拿到发表的视频,因为抖音有请求限制,所以用hook ajax请求的方式拿到数据
def _get_post_request_data2(browser,user_id,timeout,_result_):
    share_link = 'https://www.douyin.com/share/user/'+user_id+'?share_type=link'
    browser.get(share_link)
    time.sleep(timeout/2)
    #browser.execute_script(show_like)
    #post_btn = browser.find_element_by_xpath('//body/div/div[1]/div[3]/div/div[1]')
    #post_btn.click()
    # browser.execute_script(hook_ajax)
    # 滚动请求直到文档的底部
    is_bottom = False
    while (not is_bottom):
        browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        time.sleep(random.randint(7,12)/10)
        is_bottom = browser.execute_script(scroll_down)
    # 循环获取完成后拿到请求的api
    # r = browser.execute_script(get_requests_urls)
    _r = browser.execute_script("return window.finalRes")
    _result_['post'] = _r


# 拿到喜欢的视频
def _get_like_request_data(_config_,_result_):
    def get_api(user_id,count,max_cursor):
        return 'https://www.douyin.com/aweme/v1/aweme/favorite/?user_id='+user_id+'&count='+count+'&max_cursor='+max_cursor
    def _replace(r):
        return r.replace('false','False')
    st = datetime.datetime.now()
    res = []
    tmp_res = {}
    max_cursor = '0'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}
    # 第一次请求初始化一些数据
    print('>>> 请求喜欢的视频中.....')
    print('最小请求等待时间为:' + str(_config_['milt']) +'s 最大请求等待时间为:' + str(_config_['malt']) + 's')
    _r = requests.get(get_api(_config_['user_id'],_config_['slrv'],max_cursor),headers = headers)
    tmp_res['url'] = get_api(_config_['user_id'],_config_['slrv'],max_cursor)
    r = eval(_replace(_r.text))
    tmp_res['res'] = r
    res.append(tmp_res)
    tmp_res = {}
    cnt = len(r['aweme_list'])
    time.sleep(float(_config_['timeout'])/(random.randint(4,10)))
    # 循环请求
    while r['has_more'] == 1:
        t = float(_config_['timeout'])/(abs(math.sin(cnt)) * 10)
        if t < float(_config_['milt']):t = float(_config_['milt'])
        if t > float(_config_['malt']):t = float(_config_['malt'])
        time.sleep(t)
        max_cursor = str(r['max_cursor'])
        api = get_api(_config_['user_id'],_config_['slrv'],max_cursor)
        tmp_res['url'] = api
        _r = requests.get(api,headers = headers)
        r = eval(_replace(_r.text))
        tmp_res['res'] = r
        res.append(tmp_res)
        tmp_res = {}
        cnt = cnt + len(r['aweme_list'])
        print(str(cnt) + '条喜欢视频数据已添加!(随机等待时间' + str(round(t,2)) + 's)' )
    print('喜欢视频数据添加完毕,一共' + str(cnt) + '条!')
    _result_['like'] = res
    et = datetime.datetime.now()
    print('请求用时:'+ str((et - st).seconds) + 's')
    return cnt




def _download_video(_config_,_result_):
    def replace_filename(nm,n):
        str = '?*:"<>\/|\\'
        for i in str:nm = nm.replace(i,n)
        nm = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]').sub(n,nm)
        return nm
    def _download(flag,base_path): #flag is post or like
        def _sub_sownload(j,cnt):
            t = round(float(_config_['timeout'])/(abs(math.sin(cnt)) * 6),2)
            if t < float(_config_['midt']):t = float(_config_['midt'])
            if t > float(_config_['madt']):t = float(_config_['madt'])
            time.sleep(t)
            video_url = j['video']['play_addr']['url_list'][0]
            video_name = j['share_info']['share_desc']
            video_name = flag + '-' + str(cnt) + '-' + replace_filename(video_name,'_') + '.mp4'
            with open(base_path + '/' + video_name,"wb") as file:
                r = requests.get(video_url,headers = headers)
                file.write(r.content)
            print('第' + str(cnt) + '个' + flag + '视频已经下载!随机等待('+str(t)+'s) 文件为[' + video_name + ']')            
            cnt = cnt + 1
            return cnt
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}
        cnt = 1
        if flag not in _result_:return
        for i in _result_[flag]:
            if 'res' not in i or 'aweme_list' not in i['res']:continue
            for j in i['res']['aweme_list']:
                try:
                    cnt = _sub_sownload(j,cnt)
                except Exception as e:
                    print(e)
                    print('当前视频下载失败:[' + replace_filename(j['share_info']['share_desc'],'_') + ']')
        return cnt
    print('>>> 下载视频中... ...')
    print('最小请求等待时间为:' + str(_config_['midt']) +'s 最大请求等待时间为:' + str(_config_['madt']) + 's')
    base_path = _config_['download_path'] + '/' + replace_filename(_result_['title'],'-')
    if not path.exists(base_path):os.makedirs(base_path)
    print('下载路径:'+str(base_path))
    p_len = 0
    l_len = 0
    if 'post' not in _result_:
        print('没有发表的视频可供下载...')
    else:p_len = _download('post',base_path)
    if 'like' not in _result_:
        print('没有喜欢的视频可供下载...')
    else:l_len = _download('like',base_path)
    return {'p_len':p_len,'l_len':l_len}