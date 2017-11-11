# Baidu_music_crawler
Crawl baibu music info, comments and download musics and lyrics.

## Introduction

In this project, I built a Baidu music crawler, with which we can download music, crawl music ifnformation and comments. </br>
Libraries: requests, lxml, selenium. </br>
The programme arguments are as follow: </br>
'--no_categories': type=int, default=1, help='number of categories to crawl' </br>
'--no_downloads': type=int, default=20, help='number of musics to download' </br>
'--with_hot_comments': type=bool, default=False, help='crawl hot comments' </br>

## Methodology

1. Get all music tags from http://music.baidu.com/tag
2. For each tag, crawl music urls and next page urls. e.g. http://music.baidu.com/tag/%E6%96%B0%E6%AD%8C
3. For each music url, get music infos. http://music.baidu.com/song/564102115
4. For each music url, get comments and next page urls with selenium.
5. Download music.

## Result

Music info and comments are stored in sqlite database. Songs are stored in a folder.
![music](/music_info.png)
![music](/download.png)

## Reference
http://www.discoversdk.com/blog/web-scraping-with-selenium
