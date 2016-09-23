library(rvest)
library(httr)
library(stringr)
library(dplyr)

authorname=read.csv("authorname.csv",header=F, stringsAsFactors = F)[,1]
authornamelist=read.csv("authorname.csv",header=F, stringsAsFactors = F)[,2]


for(i in authornamelist){
  a=1
  dataframe=as.data.frame(matrix(ncol=4),stringsAsFactors = F)
  dataframe<-dataframe[-1,]
  searchurl=paste0('http://news.naver.com/main/search/search.nhn?query=','%BC%D2%BC%B3%B0%A1+',i,'&st=news.all&q_enc=EUC-KR&r_enc=UTF-8&r_format=xml&rp=none&sm=all.basic&ic=all&so=rel.dsc&rcnews=exist:032:020:023:025:028:038:469:&rcsection=exist:&stDate=range:20000101:20101231&detail=0&pd=4&r_cluster2_start=1&r_cluster2_display=10&start=1&display=10&startDate=2000-01-01&endDate=2010-12-31&page=')
  firstsearchpage=read_html(GET(searchurl))
  pagenum=ceiling(as.integer(str_extract(str_extract(html_text(html_nodes(firstsearchpage,'.result_num')),"\\d+건"),"\\d+"))/10)
  for(j in 1:pagenum){
    pagelist=html_attr(html_nodes(read_html(GET(paste0(searchurl,as.character(j)))),'.go_naver'),'href')
    presslist=html_text(html_nodes(read_html(GET(paste0(searchurl,as.character(j)))),'span.press'))
    l=1
    for(k in pagelist){
      newspage=read_html(GET(k))
      press=presslist[l]
      l=l+1
      title=html_text(html_nodes(newspage,'h3#articleTitle'))
      if(length(title)==0){
        next
      }
      #연예란으로 넘어갈 경우 제대로 크롤링이 되지 않기 때문에 이를 차단
      date=str_extract(html_text(html_nodes(newspage,'span.t11')),'\\d+-\\d+-\\d+')[1]
      #최초 기사 올라온 시간만 남기고 나머지 제거
      article=html_text(html_nodes(newspage,'#articleBodyContents'))
      new<-data.frame(title, date, press, article,stringsAsFactors=F)
      dataframe<-rbind(dataframe, new)
    }
  }
  write.csv(dataframe, file=paste0(authorname[a],'.csv'))
  a=a+1
}
