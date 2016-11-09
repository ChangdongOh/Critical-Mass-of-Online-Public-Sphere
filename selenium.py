# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 02:58:43 2016

@author: laman
"""

from bs4 import BeautifulSoup
import requests
import re
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas
pandas.Series  
pandas.DataFrame

dr = webdriver.Chrome()
#dr.get("http://news.naver.com/main/read.nhn?mode=LSD&mid=shm&sid1=110&oid=310&aid=0000053094&m_view=1&m_url=%2Fcomment%2Fall.nhn%3FserviceId%3Dnews%26gno%3Dnews001%2C0008731999%26sort%3Dlikability")
#dr.execute_script("var btns = document.getElementsByClassName('u_cbox_page_more');var btn = btns[0];btn.click();")
    

#키워드, 시작 날짜, 끝 날짜 지정해서 120개 이상 댓글 달린 url 가져오기
def get_newsurl(keyword, date1, date2):
    first=('http://news.naver.com/main/search/search.nhn?query={0}&st=' \
    'news.all&q_enc=EUC-KR&r_enc=UTF-8&r_format=xml&rp=none&sm=all.basic&ic=all&so=' \
    'datetime.dsc&stDate=range:20160422:20161101&detail=0&pd=4&r_cluster2_start=1&r_cluster2_display=' \
    '10&start=1&display=10&startDate={1}&endDate={2}&page=' \
    .format(urllib.parse.quote_plus(keyword.encode('cp949')),date1,date2))

    soup=BeautifulSoup(requests.get(first).text, 'lxml')
    #첫 번째 페이지를 긁어온 다음
    if soup.find('span',class_='result_num')==None:
        return []
        
    else:
        pagenum=re.sub(',','',soup.find('span',class_='result_num').text.split('건')[0].split('/')[1][1:])
        totalpage=int(int(pagenum)/10 +1)
    #html태그 구조상 전체 건수 스트링에서 '건수'에 해당하는 부분만 긁어오기 위해 정규식 사용.
    #이를 int형태로 변환한 후 나눠준 다음에 다시 소수를 정수 형태로 변환.


        i=1
        url_list=[]
        #전체 url 리스트가 담길 리스트를 만들고
        while i<=totalpage:
            pageurl=first+str(i)
            soup=BeautifulSoup(requests.get(pageurl).text, 'lxml')
        #검색 결과가 나열된 문서를 긁은 다음
            for j in soup.find_all('a',attrs={'class':'go_naver'}):
            #네이버 자체 뉴스 페이지 링크를 긁은 다음 리스트 형태로 만들고 다시 for문에 집어넣고 나서
                page=BeautifulSoup(requests.get(j.get('href')).text, 'lxml')
            #해당 페이지를 긁어버린 다음에
                if page.find('h4',class_='aside_tit')==None and page.find('div',class_='aside_photo')==None :
                #연예 기사가 아니고 스포츠 기사도 아닌 경우
                    print(j.get('href'))
                    if page.find('span',class_='lo_txt')==None:
                        continue
                    elif int(page.find('span',class_='lo_txt').text.replace(',','')) > 120:
                    #여기선 다행히 셀레늄 필요 없음
                        print(int(page.find('span',class_='lo_txt').text.replace(',','')))                    
                        url_list.append(j.get('href'))
                    else: continue
                elif page.find('h4',class_='aside_tit')==None :
                #연예 기사 아니다==스포츠 기사               
                    dr.get(j.get('href'))
                    print(j.get('href'))
                #셀레늄 활용해 해당 기사로 이동하고
                    time.sleep(0.5)
                    if BeautifulSoup(dr.page_source,"html.parser").find('span',class_='u_cbox_count') != None:
                        if BeautifulSoup(dr.page_source,"html.parser").find('span',class_='u_cbox_count').find(text=True) == None :
                            continue
                        elif int(BeautifulSoup(dr.page_source,"html.parser").find('span',class_='u_cbox_count').text.replace(',','')) > 120:
                        #댓글이 120개 이상인 경우에 리스트에 포함
                            url_list.append(j.get('href'))   
                            print(int(BeautifulSoup(dr.page_source,"html.parser").find('span',class_='u_cbox_count').text.replace(',','')))
                        else: continue    
                    else: continue
                    
                else:     
                #만일 연예 기사일 경우
                    dr.get(j.get('href'))
                    print(j.get('href'))
                #셀레늄 활용해 해당 기사로 이동하고
                    time.sleep(1)
                    if BeautifulSoup(dr.page_source,"html.parser").find('span',class_='u_cbox_count') != None:
                        if BeautifulSoup(dr.page_source,"html.parser").find('span',class_='u_cbox_count').find(text=True) == None :
                            continue
                        elif int(BeautifulSoup(dr.page_source,"html.parser").find('span',class_='u_cbox_count').text.replace(',','')) > 120:
                    #댓글이 120개 이상인 경우에 리스트에 포함
                            url_list.append(j.get('href'))   
                            print(int(BeautifulSoup(dr.page_source,"html.parser").find('span',class_='u_cbox_count').text.replace(',','')))
                        else: continue     
                    else: continue
            i+=1 
        
        return url_list
                

#네이버 뉴스의 경우 4000개 이상의 뉴스는 안 긁히게 설정되어 있으므로 한달 간격으로 나눠줌
#일단 한 해 단위로 계산한다고 가정
def seperator(keyword, date1, date2):
    
    date1ymd=date1.split('-')
    date2ymd=date2.split('-')
    dif=int(date2ymd[1])-int(date1ymd[1])
    
    i=1
    url_list=[]
    while i<dif:
        #i가 date2의 이전 월까지 계속 숫자를 늘려나가면서 한 달 단위로 url_list에 데이터 넣기를 반복
        if int(date1ymd[1])+i < 10:
            print(date1ymd[0]+'-0'+str(int(date1ymd[1])+i-1)+'-'+date1ymd[2])
            url_list+=get_newsurl(keyword, date1ymd[0]+'-0'+str(int(date1ymd[1])+i-1)+'-'+date1ymd[2], date1ymd[0]+'-0'+str(int(date1ymd[1])+i)+'-'+str(int(date1ymd[2])-1))            
            i+=1
            #중간에 0 넣어주는 것 아주아주아주 중요!
            #이 문제는 날짜에서도 영향을 줄 수 있음. 다행히 이 예시에서는 큰 문제가 안 됐으나...
        else: 
            print(date1ymd[0]+'-0'+str(int(date1ymd[1])+i-1)+'-'+date1ymd[2])
            url_list+=get_newsurl(keyword, date1ymd[0]+'-0'+str(int(date1ymd[1])+i-1)+'-'+date1ymd[2], date1ymd[0]+'-'+str(int(date1ymd[1])+i)+'-'+str(int(date1ymd[2])-1))
            i+=1
        
    url_list+=get_newsurl(keyword, date1ymd[0]+'-'+str(int(date1ymd[1])+i-1)+'-'+str(int(date1ymd[2])), date2)
    #date2가 해당하는 달에는 마지막으로 수집한 날짜에 1을 더한 날짜부터 date2까지 수집
    
    return url_list

keyword='여성혐오'
date1='2016-04-22'
date2='2016-11-01'

keywordlist=['여성혐오','성차별','메갈리아','워마드','강남역 살인','김치녀','김치남',  \
'한남충','스시녀','젠더 차별','젠더 격차']
#여혐 논란 관련 

url_list=[]

for i in keywordlist:
    print(i)
    url_list+=seperator(i, date1, date2)
    
url_list=list(set(url_list))
with open('CriticalMassofPublicOpinion/url_list.txt','w') as urltext:
    for i in url_list:
        urltext.write('%s\n' % i)
    
#총563개. 추가적으로 업데이트할 필요가 있을까?

