
# coding: utf-8

# In[2]:


###입력해주세요
era = '00년대'


# In[3]:


from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import requests
import json
import re
from selenium.common.exceptions import NoSuchElementException
import csv
import pandas as pd
from urllib.request import urlopen
import sys
import io
import glob
import os


# In[4]:


#기존 csv 파일 읽어들이기
path = r'../crawler/00년대_크롤링'                     # use your path
all_files = glob.glob(os.path.join(path, "*.csv")) 

results = []
attr_names = ['rank', 'sond_id', 'title', 'singers', 'album', 'date','genre', 'creator', 'lyric']


for f in range(len(all_files)):
    if f % 2 == 0:
        count = 0
        with open(str(all_files[f]), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if count < 10:
                    result = {}
                    result['rank'] = row['rank']
                    result['song_id'] = row['song_id']
                    result['title'] = row['title']
                    result['singers'] = row['singers']
                    result['album'] = row['album']
                    result['date'] = row['date']
                    result['genre'] = row['genre']
                    result['creator'] = row['creator']
                    result['lyric'] = row['lyric']    
                    results.append(result)
                    count += 1
                else:
                    break


# In[5]:


driver = webdriver.Chrome('./chromedriver')
driver.implicitly_wait(2)
singer_ids = []
song_sings = []
song_ids = []
additional_results = []

#song id, singer_id, debut, type, gender, company
for i in range(2610,len(results)):
    print("--------------------start-------------------------")
    song_sing = {}
    song_id = results[i]['song_id']
    
    if song_id in song_ids:
        pass
    else:
        song_ids.append(song_id)

        song_sing['song_id'] = song_id
        print("song_id : " + song_id)
        driver.get('https://www.melon.com/song/detail.htm?songId='+song_id)
        driver.implicitly_wait(5)

        additional_result = {}
        additional_result['song_id'] = song_id

        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        #불러오지 않은 정보라면

        singer_chunk = soup.select('#downloadfrm > div > div > div.entry > div.info > div.artist > a')[0]
        singer_id = str(singer_chunk).split('goArtistDetail')[1].split('"')[0].split("'")[1]
        additional_result['singer_id'] = singer_id  
        print("singer_id : " + singer_id)
        song_sing['singer_id'] = singer_id
        song_sings.append(song_sing)


        if singer_id not in singer_ids:
            singer_ids.append(singer_id)
            driver.implicitly_wait(5)
            singer_search = driver.find_element_by_xpath('//*[@id="downloadfrm"]/div/div/div[2]/div[1]/div[2]/a')
            singer_search.click()
            driver.implicitly_wait(2)
            #print("singer_search")
            detail_page = driver.find_element_by_xpath('//*[@id="conts"]/div[3]/ul/li[2]/a')
            detail_page.click()
            
            driver.implicitly_wait(5)
            #print("detail_page")

            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")
            driver.implicitly_wait(2)            
            #데뷔, 타입, 소속사명 있는 블록
            block = soup.select('#conts > div.section_atistinfo03 > dl')[0]
            block = str(block).replace('\n','')
            block = str(block).replace('\t','')
            array = str(block).split('<dt>')

            debut_num = 0
            type_num = 0
            company_num = 0

            for a in range(len(array)):
                if '데뷔' in array[a]:
                    debut_num = a
                elif '유형' in array[a]:
                    type_num = a
                elif '소속사명' in array[a]:
                    company_num = a

            if debut_num != 0:
                debut = soup.select('#conts > div.section_atistinfo03 > dl > dd:nth-of-type({})'.format(debut_num))[0].text
                #print(debut)
                if '|' in debut:
                    debut = debut.split('|')[0].replace('\n','')
                    print("debut : "+debut)
                additional_result['debut'] = debut

            if type_num != 0:
                detail = soup.select('#conts > div.section_atistinfo03 > dl > dd:nth-of-type({})'.format(type_num))[0].text
                detail = detail.replace('\n','')
                detail = detail.replace('\t','')
                detail = detail.split('|')

                singer_type = detail[0]
                singer_gender = detail[1]
                print("singer_type : "+singer_type)
                print("singer_gender : "+singer_gender)

                additional_result['singer_type'] = singer_type
                additional_result['singer_gender'] = singer_gender

            if company_num != 0:
                company = soup.select('#conts > div.section_atistinfo03 > dl > dd:nth-of-type({})'.format(company_num))[0].text
                print("company : "+company)
                additional_result['company'] = company
                
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")   
            block2 = soup.select('#conts > div.section_atistinfo04')[0]
            block2 = str(block2).replace('\n','')
            block2 = str(block2).replace('\t','')
            array2 = str(block2).split('<dt>')

            bth_num = 0
            for a in range(len(array2)):
                if '생일' in array2[a]:
                    bth_num = a
            if bth_num != 0:
                bthday = soup.select('#conts > div.section_atistinfo04 > dl > dd:nth-of-type({})'.format(bth_num))[0].text
                additional_result['bthday'] = bthday
                print("birthday : "+bthday)

            additional_results.append(additional_result)
        else:
            print("이미 가져온 가수 정보")
            pass


# In[18]:

"""
with open('./song_singer_match_{}.csv'.format(era), 'w') as csvfile:
    fieldnames = ['song_id', 'singer_id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for i in range(len(song_sings)):
        writer.writerow(song_sings[i])"""


# In[19]:


with open('./additional_result_{}.csv'.format(era), 'a') as csvfile:
    fieldnames = ['song_id', 'singer_id', 'debut', 'singer_type', 'singer_gender', 'company', 'bthday']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for i in range(len(additional_results)):
        writer.writerow(additional_results[i])



