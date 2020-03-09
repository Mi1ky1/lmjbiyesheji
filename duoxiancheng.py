import time
import requests
from bs4 import BeautifulSoup
import json
import re
import threading
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
temp_dict = {}
REG = re.compile('<[^>]*>')
lock = threading.Lock()
#请求头
headers = {
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'origin': 'https://www.zhihu.com',
    'referer': 'https://www.zhihu.com/topic/19770635/hot',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
}

class SpiderTopic(threading.Thread):

    def __init__(self, topic_item):
        threading.Thread.__init__(self)
        self.item = topic_item

lock = threading.Lock()
class SpiderTopic(threading.Thread):
    def __init__(self, topic_item):
        threading.Thread.__init__(self)
        self.item = topic_item

    def run(self):
        item = self.item
        new_url = r'www.zhihu.com/api/v4/questions/' + item[0
        ] + 'answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset=8&platform=desktop&sort_by=default'
#执行子线程 每个话题里面的回答
        #print(new_url)
        if item[1] not in temp_dict:
            temp_dict[item[1]] = []#初始化
        while True:
            try:
                html = requests.get(new_url, headers=headers)
                html.encoding = "utf8"
                data_list = html.json()['data']
                for data in data_list:
                    try:
                        q_url = data["target"]["question"]["url"]
                        lock.acquire()
                        if q_url not in temp_dict[item[1]]:
                            temp_dict[item[1]].append(q_url)
                        lock.release()
                    except Exception as e:
                        pass
                        # print(e)
                tmp_url = html.json()["paging"]["next"]
                if tmp_url == new_url:
                    break
                else:
                    new_url = tmp_url
            except Exception as e:
                break


def get_topic_nodes():
    html = requests.get(r'http://www.zhihu.com/api/v4/topics/19770635', headers=headers)#母话题“互联网招聘”的URL
    print(html.status_code)
    html.encoding = 'utf8'
    soup = BeautifulSoup(html.text, "html.parser")
    # 获取所有话题回答ID
    topic_nodes = {(item["data-href"].split("/")[2], item.text)for item in soup.findAll("li", attrs={"class":"zm-topic-cat-item"})}
    return topic_nodes

def extract_answer(s):
    temp_list = REG.sub("", s).replace("\n", "").replace(" ","")
    return temp_list

#多线程star_url应为被读取队列中的一个url
#start_url = 'https://www.zhihu.com/api/v4/questions/340937511/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B*%5D.topics&offset=&limit=3&sort_by=default&platform=desktop'
new_url=[]#多线程读取的url队列
next_url = new_url
answers = []
for url in next_url:
    html = requests.get(url, headers=headers)
    html.encoding = html.apparent_encoding
    soup = BeautifulSoup(html.text, "lxml")
    content = str(soup.p).split("<p>")[1].split("</p>")[0]
    c = json.loads(content)
    answers += [extract_answer(item["content"]) for item in c["data"] if extract_answer(item["content"]) != ""]
    next_url.append(c["paging"]["next"])
    if c["paging"]["is_end"]:
        break

for item in answers:
    print(item)
    print(len(answers))
    file = open('_data_.text','a',encoding='utf-8')
    file.write(str(answers))
    file.close()

#生成词云，中文停止词的库
def get_stopwords():
    with open("stopwords.txt", encoding='gbk') as f_stop:
        return f_stop.read().splitlines()


with open("_data_.txt", encoding="gbk") as file:
    stop_words = get_stopwords()  # 获取停止词列表
    seg_list = jieba.cut(file.read(), cut_all=False)  # 返回一个生成器
    cut_list = "/".join(seg_list).split("/")
    content_list = []
    for word in cut_list:
        if len(word.strip()) > 1 and not (word.strip() in stop_words):
            content_list.append(word)
    word_cloud = WordCloud(font_path="simsun.ttf",
                           background_color="white",
                           max_words=200,
                           max_font_size=200,
                           width=1920,
                           height=1080).generate(' '.join(content_list))

    plt.figure()  # 创建一个图形实例
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis("off")  # 不显示坐标尺寸
    plt.show()

    if __name__ == '__main__':
        s1 = time.time()
        print(s1)
        topic_nodes = get_topic_nodes()
        threading_list = [SpiderTopic(item) for item in topic_nodes]
        for thread in threading_list:
            thread.start()
        for thread in threading_list:
            thread.join()
        s2 = time.time()
        print(s2 - s1)
        s3 = time.time()
        print(s3 - s1)