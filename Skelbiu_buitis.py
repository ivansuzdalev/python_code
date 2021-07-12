import re
from lxml.html import parse
base_link = 'http://www.skelbiu.lt/skelbimai/buitis/';
base_url = 'http://www.skelbiu.lt';

page_count = 10
page_start = 1

file = open('buitis-2016-09-10.csv', 'w')

for link_ref in range(page_start,page_start+page_count):
    page = parse(base_link+str(link_ref)).getroot()

    hrefs_array = []

    hrefs_bold_area = page.find_class("boldAds")
    for row in hrefs_bold_area:
        print (row.find('a').get('href'))
        hrefs_array.append(row.find('a').get('href'))

    hrefs_normal_area = page.find_class("simpleAds")
    for row in hrefs_normal_area:
        print (row.find('a').get('href'))
        hrefs_array.append(row.find('a').get('href'))
    print(str(link_ref)+" *******************************************************************")

    for link in hrefs_array:
        print(str(link_ref)+"*******************************************************************")
 
        skelbimas = parse(base_url+link).getroot()
        sellerPhone = skelbimas.find_class("seller-phone")
        sellerLocation = skelbimas.find_class("seller-location")
        
        vardas = ""    
        miestas = ""     
        telefonas = ""
        index = 0
       
        if(len(sellerPhone)>0):
			telefonas = sellerPhone[0].text_content().encode('utf-8').strip()
        if(len(sellerLocation)>0):
		   miestas = sellerLocation[0].text_content().encode('utf-8').strip()
		   
        data_row = miestas+";"+vardas+";"+telefonas+";"+link+"\n"
            
        print(data_row)
        file.write(data_row)

file.close()




        
