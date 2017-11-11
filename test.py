from selenium import webdriver
import time

browser = webdriver.Chrome(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
browser.set_page_load_timeout(30)
browser.get('http://music.baidu.com/song/564102115')
#找到下一页按钮
page_info = browser.find_element_by_css_selector('//a[@class="page-navigator-next"]')
# print(page_info.text) 分析一下info结构
#计算出pages页码
pages = int((page_info.text.split('，')[0]).split(' ')[1])
for page in range(pages):
    #先测试一下前两页
    if page > 2:
        break
    url = 'http://music.baidu.com/song/564102115' + '#song-comment'
    browser.get(url)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(20)   # 不然会load不完整
    print(browser.getCurrentUrl())
    '''
    comments = browser.find_element_by_css_selector('找到评论信息')
    #print('测试一下评论内容')
    for comment in comments:
        try:
            detail = comment.find_element_by_css_selector('').text
            
            print(detail)
        except:
            print(comment.text)
    '''