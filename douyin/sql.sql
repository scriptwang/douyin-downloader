-- 建表语句
create table douyin(
	rid INTEGER PRIMARY KEY AUTOINCREMENT,
	aweme_id VARCHAR(255) , -- '抖音视频id,唯一'
	douyin_id VARCHAR(255) , -- '抖音作者id'
	douyin_name VARCHAR(512) , -- '抖音作者名字'
	video_url VARCHAR(255), -- '视频下载的地址'
	video_type VARCHAR(16) , -- '视频类型post or like'
	video_name VARCHAR(255), -- '视频名字'
	video_count INT, -- '视频计数'
	digg_count VARCHAR(255) , -- '点赞的数量'
	download_path VARCHAR(255) , -- '视频文件的路径'
	download_time DATETIME  -- '下载视频的时间'
);


--常用语句
select DATETIME('now');

drop table douyin;
select aweme_id from douyin;
SELECT * from douyin;
delete from douyin;

select  'post' as nm,case when max(video_count) is null then 1 else max(video_count) + 1 end as cnt,
case when max(download_time) is null then '还没下载过此小姐姐/小哥哥发表的视频呢><' else max(download_time) end as time 
from douyin where douyin_id = '65413595875' AND video_type = 'post'
UNION ALL
select  'like' as nm,case when max(video_count) is null then 1 else max(video_count) + 1 end as cnt,
case when max(download_time) is null then '还没下载过此小姐姐/小哥哥喜欢的视频呢><' else max(download_time) end as time 
from douyin where douyin_id = '65413595875' AND video_type = 'like';

select aweme_id,video_type from douyin where douyin_id = '65413595875';


