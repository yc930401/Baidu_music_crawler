import os
import json
import time
import sqlite3
import requests
import argparse
import pandas as pd
from lxml import etree
from selenium import webdriver


url = 'http://music.baidu.com'
headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'en-US,en;q=0.8,fr;q=0.6',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Cookie':'checkStatus=true; BAIDUID=B5581C3A6D8399E6E98A23F2241DA124:FG=1; PSTM=1509958702; BIDUPSID=065F54E37E17B54FDAB9C6104D3C4984; UM_distinctid=15f908d98d90-0f9cbaa1975e7e-5393662-100200-15f908d98da8f9; _user=; CNZZDATA1262632547=404369921-1509956047-http%253A%252F%252Fmusic.baidu.com%252F%7C1510064061; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; PSINO=7; H_PS_PSSID=1432_21105_18560_17001_24880_20928; app_vip=show; Hm_lvt_d0ad46e4afeacf34cd12de4c9b553aa6=1510068951,1510069089,1510069097,1510127073; Hm_lpvt_d0ad46e4afeacf34cd12de4c9b553aa6=1510127343; checkStatus=true; tracesrc=-1%7C%7Cwww.baidu.com; u_lo=0; u_id=; u_t=',
            'Host':'music.baidu.com',
            'Referer':'http://music.baidu.com/tag/%E6%96%B0%E6%AD%8C',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
           }

db_path ='/Workspace-ME/Beifeng/src/week2/homework/BaiduMusic.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()


# 1.抓取所有分类的id，然后拼接出对应的分类的链接
def get_category_urls(size):
    
    html = requests.get(url + '/tag', headers = headers)
    # Set encoding
    html.encoding = 'utf-8'
    html = html.text
    sel = etree.HTML(html)
    
    element = sel.xpath('/html/body/div/div/div/div/div/div/div/dl/dd/span/a')
    hrefs = [url + item.xpath('@href')[0] for item in element if item.xpath('@href')[0].startswith('/tag')]
    tags = [item.xpath('text()')[0] for item in element if item.xpath('@href')[0].startswith('/tag')]
    
    #indices = random.choice(len(tags), size, replace=False) # choose from top 80
    indices = [i for i in range(size)]
    result = list(zip(tags, hrefs))
    return [result[i] for i in indices]
    

# 2.访问分类的链接，抓取所有歌单（专辑）的详细页面链接

def get_album_urls(urls, album_url_dict):
    
    print(urls)
    for i in urls:
        album_urls = []
        tag, category_url = i
        html = requests.get(category_url, headers = headers).text
        sel = etree.HTML(html)
        album_urls += [url + i for i in sel.xpath('//*[@class="bb-dotimg clearfix  song-item-hook  csong-item-hook "]/div/span[4]/a[1]/@href')]
        
        try:
            next_page = url + sel.xpath('//a[@class="page-navigator-next"]/@href')[0].strip()
        except:
            print('=============== Finish crawling {}!'.format(tag))
            time.sleep(60)
        else:
            pass
            get_album_urls([(tag, next_page)], album_url_dict)
            
        album_url_dict[tag] += album_urls

    return album_url_dict

     
# 3.访问详细页面的链接，抓取所有歌曲的详细页面链接
def get_song_urls(album_urls):
    
    try:
        c.execute('DROP TABLE music_info')
    except:
        pass
    c.execute('CREATE TABLE music_info(songid, song, singer, tag, lyric_url, download_url);')
    
    count = 0
    for tag, songs in album_urls.items():
        for song in songs:
            count += 1
            print(count)
            if count % 50 == 0:
                time.sleep(60)
            songid = song.split('/')[-1]
            try:
                json = requests.get('http://tingapi.ting.baidu.com/v1/restserver/ting?method=baidu.ting.song.play&format=jsonp&songid=' + songid).json()
                print(songid, json)
            
                song = json['songinfo']['title']
                singer = json['songinfo']['author']
                lyric_url = json['songinfo']['lrclink']
                download_url = json['bitrate']['file_link']
                record = (songid, song, singer, tag, lyric_url, download_url)
                
                query_str = 'INSERT INTO music_info VALUES (%s);' % ','.join('?' * len(record))
                c.execute(query_str, record)
                print('Music_info Database updated ..')
            except:
                pass
            

# 4.抓取热门评论信息
def get_song_comments(album_urls):
    
    try:
        c.execute('DROP TABLE comments')
    except:
        pass
    c.execute('CREATE TABLE comments(com_id, songid, userid, username, ctime, comment);')
    
    count = 0
    for tag, urls in album_urls.items():
        for url in urls:
            count += 1
            print(count)
            if count % 50 == 0:
                time.sleep(60)
            print(url)
            try:
                driver.get(url)
                time.sleep(10)
                comments_all = [json.loads(element.get_attribute('data-item')) for element in driver.find_elements_by_xpath('//ul[@class="comment-list-wrap comment-list30"]/li')]
                print(comments_all)
                for comment in comments_all:
                    songid = url.split('/')[-1]
                    com_id = comment['com_id']
                    userid = comment['author']['userid']
                    username = comment['author']['username']
                    ctime = comment['ctime']
                    comment = comment['comment']
                    
                    record = (songid, com_id, userid, username, ctime, comment)
                    query_str = 'INSERT INTO comments VALUES (%s);' % ','.join('?' * len(record))
                    c.execute(query_str, record)
                    print('Comments Database updated ..')
            except:
                pass
                
            '''
            # next page
            while True:
                next_button = driver.find_element_by_xpath("//a[@class='page-navigator-next']")# '//a[@class="page-navigator-next"]'
                if next_button.get_attribute('href'):
                    driver.execute_script("arguments[0].click();", next_button)
                    #next_button.click()
                    url = driver.current_url
                    get_song_comments({tag: [url]})
                else:
                    break
            '''

    
# 5. 下载歌曲和歌词
def download_music(n):
    
    path = '/Workspace-ME/Beifeng/src/week2/homework/songs'
    
    c.execute('SELECT * from music_info limit {};'.format(n))
    results = c.fetchall()
    
    for index, result in enumerate(results):  # _ is index
        if int(index)%10 == 0:
            time.sleep(60)
        _, song, singer, tag, lyric_url, download_url = result
        print('Downoading music: Song = %s, Singer = %s, Music_url = %s, Lyric_url = %s' % (song, singer, download_url, lyric_url))
        try:
            music = requests.get(download_url, stream=True).raw.read()
            lyric = requests.get(lyric_url, stream=True).raw.read()
            file_name_music = path + '/%s-%s-%s.mp3' % (tag, song, singer)
            file_name_lyric = path + '/%s-%s-%s.lrc' % (tag, song, singer)
            if not os.path.exists('songs'):
                os.mkdir(path)
            with open(file_name_music, 'wb') as fd:
                fd.write(music)
            with open(file_name_lyric, 'wb') as fd:
                fd.write(lyric)
        except:
            print('An error occurs downloading this music !')    
        
if __name__ == '__main__':
    
    # add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--no_categories', dest='no_categories', type=int, default=1, help='number of categories to crawl')
    parser.add_argument('--no_downloads', dest='no_downloads', type=int, default=20, help='number of musics to download')
    parser.add_argument('--with_hot_comments', dest='with_hot_comments', type=bool, default=False, help='crawl hot comments')
    args = parser.parse_args()
    params = vars(args)
    
    no_categories = params['no_categories']
    no_downloads = params['no_downloads']
    with_hot_comments = params['with_hot_comments']

    album_url_dict = {item[0]:[] for item in get_category_urls(no_categories)}
    album_tags_urls = get_album_urls(get_category_urls(no_categories), album_url_dict)
    # music info
    get_song_urls(album_tags_urls)
    conn.commit()
    download_music(no_downloads)
    # comments
    if with_hot_comments:
        driver = webdriver.Chrome(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
        get_song_comments(album_tags_urls)
        conn.commit()
    conn.close()