import requests
import os
from queue import Queue
from urllib.parse import unquote
from lxml import etree

# 存放所有需要下载的文件的链接
file_urls_queue = Queue(maxsize=1000)
# 存放所有文件夹链接
dic_urls_queue = Queue(maxsize=1000)
CET = 'CET6/'


def makedir(path):
    """
    创建文件存放目录
    """
    path = CET + path
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    else:
        print("---  There is this folder:{}  ---".format(path))


def download(file_url):
    """
    下载文件
    :param file_url:
    :return:
    """
    file_url = str(file_url)
    file_url = 'https://pan.uvooc.com' + file_url
    file_name_list = file_url.split(CET)[1].split("/")
    if '' in file_name_list:
        file_name_list.remove('')
    file_name = CET
    for i in file_name_list:
        file_name = file_name + unquote(i) + '/'
    print(file_name)
    file_name = file_name[:-1]
    print("正在下载" + file_name)
    if file_url.find('.mp3') >= 0:
        try:
            r = requests.get(file_url, stream=True)
            with open(file_name, 'wb+') as m:
                m.write(r.content)
        except Exception as e:
            print('Downloading error:{}\nfile_url:{}'.format(e, file_url))
    else:
        try:
            r = requests.get(file_url)
            with open(file_name, 'wb+') as f:
                f.write(r.content)
        except Exception as e:
            print('Downloading error:{}\nfile_url:{}'.format(e, file_url))


def get_detail(dic_url):
    """
    访问dir,记录文件url
    :param dic_url:相对地址
    :return:
    """
    global file_urls_queue
    global dic_urls_queue
    local_dic_url = dic_url
    dic_url = " https://pan.uvooc.com/" + dic_url
    try:
        print("访问" + dic_url)
        request = requests.get(dic_url).text
        html = etree.HTML(request)

        # 访问dir
        dic_urls_temp_list = html.xpath('//a[@class="item" and @mimetype=""]/text()')
        # 删除返回上一页的链接
        if len(dic_urls_temp_list) > 0:
            dic_urls_temp_list.remove(dic_urls_temp_list[0])
        # 将文件夹链接存入文件夹队列并创建本地文件夹
        for i in dic_urls_temp_list:
            i = local_dic_url + i + "/"
            dic_urls_queue.put(i)
            dic_name_list = i.split(CET)[1].split("/")
            if '' in dic_name_list:
                dic_name_list.remove('')
            path = ''
            for x in dic_name_list:
                path = path + unquote(x) + '/'
            try:
                makedir(path)
            except Exception as e:
                print('dir makedir fail:{}'.format(e))

        # 记录文件url
        file_urls_temp_list = html.xpath('//a[@class="item" and @mimetype!=""]/text()')
        # 将文件链接存入文件队列
        for i in file_urls_temp_list:
            i = local_dic_url + i
            file_urls_queue.put(i)
    except Exception as e:
        print('web requests url error:: {}\nfile_url: {}'.format(e, dic_url))


def dicrun():
    while not dic_urls_queue.empty():
        get_detail(str(dic_urls_queue.get()))


def filerun():
    while not file_urls_queue.empty():
        download(file_urls_queue.get())


if __name__ == '__main__':
    init_queue = "/Learn/CET/" + CET
    dic_urls_queue.put(init_queue)
    dicrun()
    filerun()
