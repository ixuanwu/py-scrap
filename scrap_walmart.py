#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
import queue
import threading
import time

SHARE_Q = queue.Queue()  # 构造一个不限制大小的的队列
_WORKER_THREAD_NUM = 8  # 设置线程个数

service_args = [
    '--proxy=127.0.0.1:1080',
    '--proxy-type=socks5'
]

driver = webdriver.PhantomJS('D:\\phantomjs\\bin\\phantomjs.exe', service_args=service_args)
search_base_url = "https://www.walmart.com/search/?"
key_word = 'walkera'
item_infos = []


class MyThread(threading.Thread):
    def __init__(self, func):
        super(MyThread, self).__init__()
        self.func = func

    def run(self):
        self.func()


def worker():
    global SHARE_Q
    while not SHARE_Q.empty():
        item = SHARE_Q.get()  # 获得任务
        item_info = getItemInfo(item)
        item_infos.append(item_info)
        time.sleep(1)


def main():
    global SHARE_Q
    threads = []
    for i in range(8):
        page = str(i + 1)
        putItemUrls(getSearchUrl(page, key_word))
    for i in range(_WORKER_THREAD_NUM):
        thread = MyThread(worker)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    print(item_infos)


def getSearchUrl(page, key_word):
    return search_base_url + 'page=' + page + '&query=' + key_word


def getItemInfo(item_url):
    driver.get(item_url)
    brand_url = driver.find_element_by_css_selector('.prod-BrandName').get_attribute('href')
    index = brand_url.rfind('/') + 1
    brand_name = brand_url[index:]
    seller_fulfillment = driver.find_element_by_css_selector('.prod-SellerFulfillmentSection').text
    item_info = {
        'brand_url': brand_url,
        'brand_name': brand_name,
        'seller_fulfillment': seller_fulfillment,
        'item_url': item_url
    }
    print(item_info)
    return item_info


def putItemUrls(search_url):
    driver.get(search_url)
    searchResultLists = driver.find_elements_by_css_selector(
        '.search-result-listview-items .search-result-productimage a')
    for searchResultList in searchResultLists:
        item_url = searchResultList.get_attribute('href')
        if (item_url):
            SHARE_Q.put(item_url)


if __name__ == '__main__':
    main()
