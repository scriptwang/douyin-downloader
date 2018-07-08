//!important 一定要把数据绑定在window或别的浏览器本来就有的对象上面,直接定义变量在最后selenium拿不到
window.finalRes = [];
(function(send,open){
    var self = this;
    self.tmp = {};
    XMLHttpRequest.prototype.open = function(method, url, async, user, pass) {
        if (url.indexOf('aweme/v1/aweme/post') != -1) self.tmp.url = url;/*发请求之前拦截*/
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