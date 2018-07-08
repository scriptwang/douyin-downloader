# -*- coding:utf-8 -*-

# js:注册函数
rigister_function = '''
    //拿到请求后记录的请求
    window.getRequestsUrl = function(){
        var r = [];
        var n = window.performance.getEntries();
        for(i in n){
            if (n[i].initiatorType == 'xmlhttprequest' && n[i].name.indexOf('aweme/v1/aweme/post') != -1){
                r.push(n[i].name)
            }
        }
        return r;
    }

    //Xpath 寻找元素
    window.getElementByXpath = function (STR_XPATH) {
        var xresult = document.evaluate(STR_XPATH, document, null, XPathResult.ANY_TYPE, null);
        var xnodes = [];
        var xres;
        while (xres = xresult.iterateNext()) {
            xnodes.push(xres);
        }
        return xnodes;
    }
    
    //Hook Ajax 注入ajax对象代码
    //!important 一定要把数据绑定在window或别的浏览器本来就有的对象上面,直接定义变量在最后selenium拿不到
    window.finalRes = [];
    (function(send,open){
        var self = this;
        self.tmp = {};
        XMLHttpRequest.prototype.open = function(method, url, async, user, pass) {
            if (url.indexOf('aweme/v1/aweme/post') != -1)  self.tmp.url = url;
            open.call(this, method, url, async, user, pass);
        };
        XMLHttpRequest.prototype.send = function (data) {
            this.addEventListener("readystatechange", function(){
                if( this.readyState == 4 /* complete */) {/*发请求之后拦截*/
                    var j = eval('(' + this.responseText + ')');
                    //有可能后发出去的请求会先返回结果,所以对返回数据进行判断
                    if ('has_more' in j && 'status_code' in j){
                        self.tmp.res = j;
                        window.finalRes.push(self.tmp);
                        self.tmp = {};
                    }
                }
            }, false);
            send.call(this, data);
        }
    })(XMLHttpRequest.prototype.send,XMLHttpRequest.prototype.open);

    //计算请求到数据的长度
    window.resCnt = function(){
        var cnt = 0;
        for (i in window.finalRes){
            cnt = cnt + window.finalRes[i].res.aweme_list.length
        }
        return cnt;
    }
'''

# js:页面滚动到喜欢/作品按钮的位置
show_like = '''
    //找到喜欢按钮元素
    likeBtn = window.getElementByXpath('//body/div/div[1]/div[3]/div/div[2]')[0]
    //向下滚动页面直至喜欢按钮出现在页面上,为后面点击喜欢按钮做准备
    var is_show = false;
    var clientHeight = window.document.documentElement.clientHeight;
    var p = 0;
    while (!is_show){
        window.scrollTo(0,p);
        p += 10;//每次步进10
        if (likeBtn.getBoundingClientRect().top - clientHeight < -(likeBtn.offsetHeight + 100)) {
            is_show = true     
        }
    }
'''

# js屏幕向下滚动
scroll_down = '''
    //document文档的总高度
    var docHeight = document.documentElement.scrollHeight;
    //文档上部超出浏览器的高度
    var scrollTop = (document.documentElement && document.documentElement.scrollTop) || document.body.scrollTop;
    //浏览器窗口的高度
    var clientHeight = window.document.documentElement.clientHeight;
    //判断是否到了文档底部
    return scrollTop + clientHeight == docHeight;
'''

# 最后请求第一个ajax请求,并放在数组第一位
final_ajax = '''
    requests = window.getRequestsUrl();
    var ajax = new XMLHttpRequest();
    console.log(requests[0])
    ajax.open('get',requests[0],false);
    ajax.send();
    ajax.onreadystatechange = function () {
        if (ajax.readyState==4 &&ajax.status==200) {
            //步骤五 如果能够进到这个判断 说明 数据 完美的回来了,并且请求的页面是存在的
            var r = {};
            r.url = requests[0];
            r.res = eval('(' + ajax.responseText + ')');
            window.finalRes.push(r)
            //??
            //var tmp = [r];
            //window.finalRes = tmp.concat(window.finalRes);
    　　}
    }
'''