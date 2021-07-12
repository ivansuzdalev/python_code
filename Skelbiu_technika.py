import re
from lxml.html import parse
base_link = 'http://www.skelbiu.lt/skelbimai/technika/';

page_count = 100
page_start = 1

file = open('technika-2016-09-11.csv', 'w')

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
 
        skelbimas = parse(base_link+link).getroot()

        sellerAreaFirst = skelbimas.find_class("sellerAreaFirst")
        sellerAreaSecondCity = skelbimas.find_class("sellerAreaSecondCity")
        sellerAreaSecond = skelbimas.find_class("sellerAreaSecond")

        if(len(sellerAreaFirst)>0 and len(sellerAreaSecondCity)>0 and len(sellerAreaSecond)>0):
            vardas = ""
            miestas = ""
            if(len(sellerAreaSecondCity)>0):
                miestas = sellerAreaSecondCity[0].text_content()
            telefonas = ""
            index = 0

            for cell in sellerAreaFirst:
                if  "Telefonas" in cell.text_content():
                    telefonas = sellerAreaSecond[index].text_content()
                if  "Vardas" in cell.text_content():
                    vardas = sellerAreaSecond[index].text_content()
                index = index + 1
            data_row = miestas+";"+vardas+";"+telefonas+";"+link+"\n"
            
            print(data_row)
            file.write(data_row)

file.close()




        
