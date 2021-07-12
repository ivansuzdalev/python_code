import re
from lxml.html import parse
import lxml.html as html
base_link = 'http://www.skelbiu.lt/skelbimai/skelbimai/skelbimai/skalbimo-masinu-remontas-vilniuje-19465210.html';

page = parse(base_link).getroot()

sellerAreaFirst = page.find_class("sellerAreaFirst")
sellerAreaSecondCity = page.find_class("sellerAreaSecondCity")
sellerAreaSecond = page.find_class("sellerAreaSecond")

if(len(sellerAreaFirst)>0 and len(sellerAreaSecondCity)>0 and len(sellerAreaSecond)>0):
    miestas = ""
    if(len(sellerAreaSecondCity)>0):
        miestas = sellerAreaSecondCity[0].text_content()
    telefonas = ""
    index = 0

    for cell in sellerAreaFirst:
        if  "Telefonas" in cell.text_content():
            telefonas = sellerAreaSecond[index].text_content()
        index = index + 1

    print(miestas)
    print(telefonas)
