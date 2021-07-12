'''
Algoritmas yra skirtas nuskaityti atvaizdus padarytus iš DJI MAVIC PRO šiluminio
ir visualinio spektro kamerų. Atvaizdai yra nuskaitomi iš vieno aplanko. Atvaizdai
tūri kartotis poromis "visualinis spenktas / šiluminis spektras". Lyginiai atvaizdai
yra laikomi šiluminiais, nelyginiai visualiais. Kadangi MAVIC šiluminės kamėros
skiriamoji geba skiriasi nuo vizualinio spektro kameros skiriamosios gebos be to skiriasi
ir apertūros kampas, reikia apkarpyti visualinio spektro atvaizdą bei pakeisti jo skyriamąją
gebą. Vizualinis ir šiluminis atvaizdas kerpami pagal kvadrantus ir kvadrantai saugomi
į duomenų bazę.


'''
import sqlite3
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from datetime import datetime
import cv2
import numpy as np
import pylab
from os import listdir
from os.path import isfile, join
from numpy import asarray
import json

# Metodas verčiantis paveikslo pikselių seką vienmačiu masyvu
def imgToArr(image):
    img_arr = []
    for line in image:
        for pixel in line:
            img_arr.append(int(pixel[0]))
            img_arr.append(int(pixel[1]))
            img_arr.append(int(pixel[2]))

    return img_arr

# inicijuojama duomenų bazė
conn = sqlite3.connect('ir.db')
c = conn.cursor()

# Sukuriame reikiamą lentelę saugoti duomenys
c.execute('''CREATE TABLE IF NOT EXISTS ir_data
                 (id INTEGER PRIMARY KEY, folder_name text, visual_filename text, thermal_filename text, image_cropped text, x_coord text, y_coord text, mean_visual text, mean_thermal text)''')
#iš šito aplanko bus nuskaitomi visualiniai bei termaliniai atvaizdai
folder_name = 'datasets'

#atvaizdų nuskaitymas
files = [f for f in listdir(folder_name) if isfile(join(folder_name, f))]
#Išrušiuojame atvaizdus pagal vardus
files = sorted(files)

print(files)
#daliklis dalių į kurias bus karpomas paveiklas. Pvz prie daliklio 20x20 bus 400 dalių
divider = 20

#Perrenkami visi atvaizdų
for index in range(1, len(files), 2):
    #Nuskaitomas šiluminio atvaizdo pavadinimas
    thermal_filename = files[index]
    #Nuskaitomas visualinio atvaizdo pavadinimas
    visual_filename = files[index-1]
    
    print('thermal '+thermal_filename)
    print('visual '+visual_filename)

    #Nuskaitomas visulinis atvaizdas
    thermal_img = cv2.imread('datasets/' + thermal_filename)
    
    thermal_height = thermal_img.shape[0]
    thermal_width = thermal_img.shape[1]

    #Nuskaitomas termalinis atvaizdas
    visual_img = cv2.imread('datasets/' + visual_filename)
    visual_height = visual_img.shape[0]
    visual_width = visual_img.shape[1]    

    #Apkerpamas vizualinis atvaizdas
    crop_visual_img = visual_img[452:visual_height-180, 504:visual_width - 340]
    #Visualinis atvaizdas pagal išmatavimus suvienodinamas su šiluminiu atvaizdu
    visual_img = cv2.resize(crop_visual_img,(thermal_width, thermal_height))
    visual_height = visual_img.shape[0]
    visual_width = visual_img.shape[1]
    
    print(thermal_height, thermal_width)
    print(visual_height, visual_width)

    #Nustatomas vieno atvaizdo gabaliuko aukštis ir plotis
    h = int(thermal_height / divider)
    w = int(thermal_width / divider)
                
    if thermal_height == visual_height and thermal_width == visual_width and thermal_width == 640 and thermal_height == 480:

        #Šiluminis ir visualinis atvaizdai perrenkami po gabaliuką
        for x in range(0,thermal_width-w, w):
            for y in range(0,thermal_height-h,h):
                crop_visual_img = visual_img[y:y+h, x:x+w]
                print(crop_visual_img.shape)
                crop_thermal_img = thermal_img[y:y+h, x:x+w]
                print(crop_thermal_img.shape)
                visual_data_cropped = imgToArr(crop_thermal_img)
                #mean_thermal = cv2.mean(crop_thermal_img)

                #Nustatomos atvaizdų gabaliukų vidūdinės spalvų reikšmės
                mean_thermal = crop_thermal_img.mean()
                mean_visual = cv2.mean(crop_visual_img)
                #Kiekvienas paveikslo gabaliukas verčiamas JSON formatu ir įrašomas į duomenų bazę
                cropped_image_json = json.dumps(visual_data_cropped)
                #to_array_json = json.loads(cropped_image_json)
                c.execute("INSERT INTO ir_data(folder_name, visual_filename, thermal_filename, image_cropped, x_coord, y_coord, mean_visual, mean_thermal) VALUES('" + folder_name + "','" + visual_filename  + "', '" + thermal_filename +"', '" + cropped_image_json +"', '" + str(x) +"', '" + str(y) +"', '" + str(mean_visual) +"', '" + str(mean_thermal) +"');")

                #print(mean_visual, mean_thermal)
                #cv2.imshow('croped', crop_visual_img)
        print('writed to DB')
                
    else:
        print('different resolution in imgaes')
        

    #cv2.imshow('thermal', thermal_img)
    #cv2.imshow('visual', visual_img) 
    #waits for user to press any key  
    #(this is necessary to avoid Python kernel form crashing) 
    cv2.waitKey(0)  
      
    #closing all open windows  
    cv2.destroyAllWindows()



