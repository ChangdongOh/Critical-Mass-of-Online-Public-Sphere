# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 02:49:53 2016

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

#셀레늄으로 url_list에서 읽어와 직접 댓글까지 한꺼번에 읽어오는 작업 시작. 
#일반 기사, 연예 기사, 스포츠 기사로 분리하고
#왜 특정 기사에서는 공감순과 최신순만 먹히는 것인지 알아봐야. 현재로서는 2~3일 정도 텀이 필요할 것으로 보임.
#게다가 네이버 댓글은 24시간 이상 지나지 않으면 'n시간 전'으로 표기됨.
#soup.find_all('div', id='articleBodyContents')로 본문 내용 읽어온 다음에 내부 
#태그들 가운데서 href 달린 외부 링크 내용만 잘라내면 언론사 광고 등등 제거 가능.
#온라인데이터수업 네이버 크롤링 참조  

dr = webdriver.Chrome()

def extractarticle(url):
    print(url)
    soup=BeautifulSoup(requests.get(url).text, 'lxml')
    time.sleep(1)
    
    if soup.find('h4',class_='aside_tit')==None and soup.find('div',class_='aside_photo')==None :
        dr.get(url)   
        time.sleep(1)
        press=soup.find('div', class_='press_logo').find('img')['title']
        article=soup.find('div',attrs={'id':'articleBodyContents'}).text        
        for i in soup.find('div',attrs={'id':'articleBodyContents'}).find_all('a'):
            article=article.replace(i.text,' ')
        
        pubtime=soup.find('span',class_='t11').text
        dr.find_element_by_css_selector('span.lo_txt').click()
        time.sleep(2)
        soup=BeautifulSoup(dr.page_source,"html.parser")
        #시간 딜레이 안 넣어주면 뻗음
        
        sexratio=float(soup.find('span',class_='u_cbox_chart_per').find(text=True)[:-1])/100
        generationratio=[]
        j=2
        while j < 7 :
            generationratio.append(float(soup.find_all('span',class_='u_cbox_chart_per')[j].text[:-1])/100)
            j+=1
        
        #한번 눌러줄 때마다 20개씩 추가적으로 댓글 띄워지므로 몇 번 누를지 계산
        count=int(re.sub(',','',soup.find('span',class_='u_cbox_count').text))
        #더 누르기 버튼
        more=dr.find_element_by_css_selector('.u_cbox_page_more')

        k=0
        while k < int((count-1)/20):
            more.click()
            time.sleep(1+k/100)
            #시간 딜레이 안 넣어주면 뻗음
            print(k)
            k+=1
            
        dr.find_element_by_tag_name('body').send_keys(Keys.UP) 
        time.sleep(0.3)

        #페이지가 업데이트 되었으므로 다시 page_source를 가져와서 파싱
        commsoup=BeautifulSoup(dr.page_source,"html.parser").find_all('div',class_='u_cbox_area')
        
        
        commentslist=[]
        
        l=0
        while l < count:
            
            comarea=commsoup[l]
            #sns는 페북/트위터 각각 태그가 달라서 if로 분류
            if comarea.find('span',class_='u_cbox_sns_icons u_cbox_sns_facebook') != None:
                sns='1'
            elif comarea.find('span',class_='u_cbox_sns_icons u_cbox_sns_twitter') != None:
                sns='2'
            else: sns='0'

            name=comarea.find('span',class_='u_cbox_nick').text
            body=comarea.find('span',class_='u_cbox_contents').text
            date=comarea.find('span',class_='u_cbox_date').text
            favor=int(comarea.find('em',class_='u_cbox_cnt_recomm').text)
            oppose=int(comarea.find('em',class_='u_cbox_cnt_unrecomm').text)
            print('%s %s' % (str(l+1),name) )
            #해당 댓글의 전체 답글 수 카운트
            repcount=int(comarea.find('span',class_='u_cbox_reply_cnt').text)           

            
            replylist=[]
            repnamelist=[]

            if repcount==0:
                pass
            elif repcount>20:
                
                replybtn=dr.find_element_by_xpath("//div[@id='cbox_module']/div/div[6]/ul/li["+str(l+1)+"]/div/div/div[4]/a")
                time.sleep(1) 
                replybtn.click()    
                time.sleep(1) 
                
                replymore=dr.find_element_by_css_selector("span.u_cbox_box_more > span.u_cbox_page_more")

                #같은 액션 반복시에는 _변수 사용
                for _ in range(0, int((repcount-1)/20)):
                    replymore.click()
                    time.sleep(1)  
                
                #태그 구조상 직접 긁어오면 답글과 댓글이 겹치므로 navigate 쓰는게 안전
                repsoup=BeautifulSoup(dr.page_source,"html.parser").find_all('span',class_='u_cbox_ico_reply')
                    
                n=0
                while n < repcount:
                    replylist.append(repsoup[n].next_sibling.find('span',class_='u_cbox_nick').text)
                    repnamelist.append(repsoup[n].next_sibling.find('span',class_='u_cbox_contents').text)
                    n+=1
                    

                dr.find_element_by_tag_name('body').send_keys(Keys.UP) 
                replybtn=dr.find_element_by_css_selector("a.u_cbox_btn_reply.u_cbox_btn_reply_on > span.u_cbox_reply_cnt")
                time.sleep(1) 
                replybtn.click()    
                time.sleep(1) 
                
            else:
                replybtn=dr.find_element_by_xpath("//div[@id='cbox_module']/div/div[6]/ul/li["+str(l+1)+"]/div/div/div[4]/a")
                time.sleep(1) 
                replybtn.click()    
                time.sleep(1)                 
                
                repsoup=BeautifulSoup(dr.page_source,"html.parser").find('ul',class_='u_cbox_list')
                repnames=repsoup.find_all('span',class_='u_cbox_nick')
                reps=repsoup.find_all('span',class_='u_cbox_contents')
                n=0
                while n < repcount:
                    replylist.append(reps[n].text)
                    repnamelist.append(repnames[n].text)
                    n+=1
                #끝나고 나서는 깔끔하게 답글창은 다시 닫아주기

                dr.find_element_by_tag_name('body').send_keys(Keys.UP) 
                replybtn=dr.find_element_by_css_selector("a.u_cbox_btn_reply.u_cbox_btn_reply_on > span.u_cbox_reply_cnt")
                time.sleep(1) 
                replybtn.click()    
                time.sleep(1) 
             
            
            commentslist.append([name, sns, body, date, favor, oppose, repcount,repnamelist, replylist])   
            l+=1
            
            
#==============================================================================
# 스포츠면
#==============================================================================

    elif soup.find('h4',class_='aside_tit')==None:
        
        press=soup.find('span', class_='logo').find('img')['alt']
        articlelist=soup.find_all('p')
        article=''
        for h in articlelist:
            if h.find('a') == None:
                article+=h.text
            else: pass
        
        pubtime=re.sub('[.]','-', re.compile('\d{4}[.]\d{2}[.]\d{2}'). \
        findall(soup.find('div',class_='info').find_all('span')[1].text)[0])      
        
        newurl=url+'&m_view=1'
        dr.get(newurl)
        time.sleep(2)
        soup=BeautifulSoup(dr.page_source,"html.parser")
        #시간 딜레이 안 넣어주면 뻗음
        sexratio=float(soup.find('span',class_='u_cbox_chart_per').find(text=True)[:-1])/100
        generationratio=[]
        j=2
        while j < 7 :
            generationratio.append(float(soup.find_all('span',class_='u_cbox_chart_per')[j].text[:-1])/100)
            j+=1
        
        #한번 눌러줄 때마다 20개씩 추가적으로 댓글 띄워지므로 몇 번 누를지 계산
        count=int(re.sub(',','',soup.find('span',class_='u_cbox_count').text))
        #더 누르기 버튼
        more=dr.find_element_by_css_selector('.u_cbox_page_more')

        k=0
        while k < int((count-1)/20):
            more.click()
            time.sleep(1+k/100)
            #시간 딜레이 안 넣어주면 뻗음
            print(k)
            k+=1
            
        dr.find_element_by_tag_name('body').send_keys(Keys.UP) 
        time.sleep(0.3)
        
        #페이지가 업데이트 되었으므로 다시 page_source를 가져와서 파싱
        commsoup=BeautifulSoup(dr.page_source,"html.parser").find_all('div',class_='u_cbox_area')
        
        commentslist=[]
        
        l=0
        while l < count:
            comarea=commsoup[l]
            #sns는 페북/트위터 각각 태그가 달라서 if로 분류
            if comarea.find('span',class_='u_cbox_sns_icons u_cbox_sns_facebook') != None:
                sns='1'
            elif comarea.find('span',class_='u_cbox_sns_icons u_cbox_sns_twitter') != None:
                sns='2'
            else: sns='0'

            name=comarea.find('span',class_='u_cbox_nick').text
            body=comarea.find('span',class_='u_cbox_contents').text
            date=comarea.find('span',class_='u_cbox_date').text
            favor=int(comarea.find('em',class_='u_cbox_cnt_recomm').text)
            oppose=int(comarea.find('em',class_='u_cbox_cnt_unrecomm').text)
            print('%s %s' % (str(l+1),name) )
            
            #해당 댓글의 전체 답글 수 카운트
            repcount=int(comarea.find('span',class_='u_cbox_reply_cnt').text)           
            
            replylist=[]
            repnamelist=[]

            if repcount==0:
                pass
            elif repcount>20:

                replybtn=dr.find_element_by_xpath("//div[@id='cbox_module']/div/div[6]/ul/li["+str(l+1)+"]/div/div/div[4]/a")
                time.sleep(1) 
                replybtn.click()    
                time.sleep(1)

                replymore=dr.find_element_by_css_selector("span.u_cbox_box_more > span.u_cbox_page_more")
                #같은 액션 반복시에는 _변수 사용
                for _ in range(0, int((repcount-1)/20)):
                    replymore.click()
                    time.sleep(1)
                    
                #태그 구조상 직접 긁어오면 답글과 댓글이 겹치므로 navigate 쓰는게 안전
                repsoup=BeautifulSoup(dr.page_source,"html.parser").find_all('span',class_='u_cbox_ico_reply')
                    
                n=0
                while n < repcount:
                    replylist.append(repsoup[n].next_sibling.find('span',class_='u_cbox_nick').text)
                    repnamelist.append(repsoup[n].next_sibling.find('span',class_='u_cbox_contents').text)
                    n+=1
                        
                dr.find_element_by_tag_name('body').send_keys(Keys.UP) 
                replybtn=dr.find_element_by_xpath("//div[@id='cbox_module']/div/div[6]/ul/li["+str(l+1)+"]/div/div/div[4]/a")
                time.sleep(1) 
                replybtn.click()    
                time.sleep(1) 
            else:
                
                replybtn=dr.find_element_by_xpath("//div[@id='cbox_module']/div/div[6]/ul/li["+str(l+1)+"]/div/div/div[4]/a")
                time.sleep(1) 
                replybtn.click()    
                time.sleep(1)                
                
                repsoup=BeautifulSoup(dr.page_source,"html.parser").find('ul',class_='u_cbox_list')
                repnames=repsoup.find_all('span',class_='u_cbox_nick')
                reps=repsoup.find_all('span',class_='u_cbox_contents')
                n=0
                while n < repcount:
                    replylist.append(reps[n].text)
                    repnamelist.append(repnames[n].text)
                    n+=1
                #끝나고 나서는 깔끔하게 답글창은 다시 닫아주기
                
                dr.find_element_by_tag_name('body').send_keys(Keys.UP) 
                replybtn=dr.find_element_by_xpath("//div[@id='cbox_module']/div/div[6]/ul/li["+str(l+1)+"]/div/div/div[4]/a")
                time.sleep(1) 
                replybtn.click()    
                time.sleep(1)   
              
            
            commentslist.append([name, sns, body, date, favor, oppose, repcount,repnamelist, replylist])   
            l+=1      
            
    
#==============================================================================
# 연예면    
#==============================================================================
    
    else:    
        url='http://entertain.naver.com/read?'+url[-22:]
        press=soup.find('div', class_='press_logo').find('img')['alt']
        article=soup.find('div',attrs={'id':'articeBody'}).text        
        for i in soup.find('div',attrs={'id':'articeBody'}).find_all('a'):
            article=article.replace(i.text,' ')
        
        pubtime=re.sub('[.]','-', re.compile('\d{4}[.]\d{2}[.]\d{2}'). \
        findall(soup.find('span',class_='author').find('em').text)[0])      

        newurl=re.sub('read','comment/list',url)
        dr.get(newurl)
        time.sleep(2)
        
        soup=BeautifulSoup(dr.page_source,"html.parser")
        #시간 딜레이 안 넣어주면 뻗음
        sexratio=float(soup.find('span',class_='u_cbox_chart_per').find(text=True)[:-1])/10
        generationratio=[]
        j=2
        while j < 7 :
            generationratio.append(float(soup.find_all('span',class_='u_cbox_chart_per')[j].text[:-1])/100)
            j+=1
        
        #한번 눌러줄 때마다 20개씩 추가적으로 댓글 띄워지므로 몇 번 누를지 계산
        count=int(re.sub(',','',soup.find('span',class_='u_cbox_count').text))
        #더 누르기 버튼
        more=dr.find_element_by_css_selector('.u_cbox_page_more')

        k=0
        while k < int((count-1)/20):
            more.click()
            time.sleep(1+k/100)
            #시간 딜레이 안 넣어주면 뻗음
            print(k)
            k+=1
         
        dr.find_element_by_tag_name('body').send_keys(Keys.UP) 
        time.sleep(0.3)
        
        
        #페이지가 업데이트 되었으므로 다시 page_source를 가져와서 파싱
        commsoup=BeautifulSoup(dr.page_source,"html.parser").find_all('div',class_='u_cbox_area')
       
        commentslist=[]
        
        l=0
        
        while l < count:
            comarea=commsoup[l]
            #sns는 페북/트위터 각각 태그가 달라서 if로 분류
            if comarea.find('span',class_='u_cbox_sns_icons u_cbox_sns_facebook') != None:
                sns='1'
            elif comarea.find('span',class_='u_cbox_sns_icons u_cbox_sns_twitter') != None:
                sns='2'
            else: sns='0'

            name=comarea.find('span',class_='u_cbox_nick').text
            body=comarea.find('span',class_='u_cbox_contents').text
            date=comarea.find('span',class_='u_cbox_date').text
            favor=int(comarea.find('em',class_='u_cbox_cnt_recomm').text)
            oppose=int(comarea.find('em',class_='u_cbox_cnt_unrecomm').text)
            print('%s %s' % (str(l+1),name) )
            
            #해당 댓글의 전체 답글 수 카운트
            repcount=int(comarea.find('span',class_='u_cbox_reply_cnt').text)           

            
            replylist=[]
            repnamelist=[]

            if repcount==0:
                pass
            
            elif repcount>20:
                #답글 펼치기
                #연예면은 일반 기사와는 달리 div[7]이었음. 에혀...                
                replybtn=dr.find_element_by_xpath("//div[@id='cbox_module']/div/div[7]/ul/li["+str(l+1)+"]/div/div/div[4]/a")
                time.sleep(1) 
                replybtn.click() 
                time.sleep(1)      
                
                replymore=dr.find_element_by_css_selector("span.u_cbox_box_more > span.u_cbox_page_more")

                #같은 액션 반복시에는 _변수 사용
                for _ in range(0, int((repcount-1)/20)):
                    replymore.click()
                    time.sleep(1)
                    
                #태그 구조상 직접 긁어오면 답글과 댓글이 겹치므로 navigate 쓰는게 안전
                repsoup=BeautifulSoup(dr.page_source,"html.parser").find_all('span',class_='u_cbox_ico_reply')
                    
                n=0
                while n < repcount:
                    replylist.append(repsoup[n].next_sibling.find('span',class_='u_cbox_nick').text)
                    repnamelist.append(repsoup[n].next_sibling.find('span',class_='u_cbox_contents').text)
                    n+=1
                    
                    
                dr.find_element_by_tag_name('body').send_keys(Keys.UP) 
                time.sleep(0.3)
                
                replybtn=dr.find_element_by_css_selector("a.u_cbox_btn_reply.u_cbox_btn_reply_on > span.u_cbox_reply_cnt")
                time.sleep(1) 
                replybtn.click()
                time.sleep(1)           
                
            else:
                replybtn=dr.find_element_by_xpath("//div[@id='cbox_module']/div/div[7]/ul/li["+str(l+1)+"]/div/div/div[4]/a")
                time.sleep(1)
                replybtn.click() 
                time.sleep(1)
                
                repsoup=BeautifulSoup(dr.page_source,"html.parser").find('ul',class_='u_cbox_list')                
                repnames=repsoup.find_all('span',class_='u_cbox_nick')
                reps=repsoup.find_all('span',class_='u_cbox_contents')
                n=0
                while n < repcount:
                    replylist.append(reps[n].text)
                    repnamelist.append(repnames[n].text)
                    n+=1
                #끝나고 나서는 깔끔하게 답글창은 다시 닫아주기
                dr.find_element_by_tag_name('body').send_keys(Keys.UP) 
                time.sleep(0.3)
                
                replybtn=dr.find_element_by_css_selector("a.u_cbox_btn_reply.u_cbox_btn_reply_on > span.u_cbox_reply_cnt")
                time.sleep(1) 
                replybtn.click()    
                time.sleep(1)             
            
            commentslist.append([name, sns, body, date, favor, oppose, repcount,repnamelist, replylist])   
            l+=1
            
        
    totallist=[press, article, pubtime, sexratio, generationratio, commentslist]
    return totallist
       
        
with open('CriticalMassofPublicOpinion/url_list.txt', 'r') as urltext:
    with open('result.txt','a', encoding='UTF8') as f: 
        url_list=urltext.read().split('\n')[29:-1]
        for i in url_list:
            f.write('%s\n' % extractarticle(i))
            
        
        
