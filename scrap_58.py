#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import Request,urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup

base_url = "http://m.58.com"
city_url = base_url+'/city.html'
file = 'user_profile.txt'

def addHeader(request):
    request.add_header('User-Agent','Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1')
    request.add_header('Referer', 'http://m.58.com/city.html?from=click_city_new&return=http://m.58.com/sz/zufang')
    return request

def getCityList():
    req = Request(city_url)
    req = addHeader(req)
    cityLists = []
    new_city_lists = []
    try:
        response = urlopen(req)
        bsObj = BeautifulSoup(response.read(), "html.parser")
        cityListNodes = bsObj.select('.city_lst li a')
        for cityListNode in cityListNodes:
            href = cityListNode['href']
            index = href.find('//',7)
            cityLists.append(href[0:index])
        new_city_lists = list(set(cityLists))
        new_city_lists.sort(key=cityLists.index)
    except HTTPError as e:
        print(e)
    return new_city_lists

def getInfoIds(url):
    req = Request(url)
    req = addHeader(req)
    infoIds = []
    try:
        response = urlopen(req)
        bsObj = BeautifulSoup(response.read(), "html.parser")
        nodeList = bsObj.select('.infoList li')
        for list in nodeList:
            infoIds.append(list['infoid'])
        return infoIds
    except HTTPError as e:
        print(e)

def getUserProfile(url):
    req = Request(url)
    req = addHeader(req)
    name = None
    mobile = None
    try:
        response = urlopen(req)
        bsObj = BeautifulSoup(response.read(), "html.parser")
        user_profile = bsObj.select('.user-profile')
        if(user_profile):
            user_profile = user_profile[0]
            nameNode = user_profile.find('span', class_='profile-name')
            if (nameNode):
                name = nameNode.get_text().strip()
            mobileNode = user_profile.find('span', class_='meta-phone')
            if (mobileNode):
                mobile = mobileNode.get_text().strip()
    except HTTPError as e:
        print(e)
    return {"name": name, "mobile": mobile}

def write_a_file(file,content):
    with open(file, 'a+') as f:
        f.write(content)
        f.close()

cityLists = getCityList()
for city in cityLists:
    print(city)
    zufang_url = city+'/zufang/'
    infoIds = getInfoIds(zufang_url)
    print(infoIds)
    for infoId in infoIds:
        mob_url = zufang_url + infoId + 'x.shtml'
        userProfile = getUserProfile(mob_url)
        if (userProfile['mobile']):
            userProfile['infoId'] = infoId
            print(userProfile)
            str = '\t'.join(userProfile.values()) + '\n'
            write_a_file(file,str)
