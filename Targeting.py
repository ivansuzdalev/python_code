import cv2
import skvideo.io
import imutils
import numpy as np
from filterpy.kalman import MerweScaledSigmaPoints
from filterpy.kalman import UnscentedKalmanFilter
from filterpy.common import Q_discrete_white_noise

##************************************************************************************************************************
##ОСНОВНЫЕ НАСТРОЙКИ АЛГОРИТМА. ЕСЛИ ПЛОХО РАБОТАЕТ В КАКИХ ЛИБО УСЛОВИЯХ, КРУТИМ В ПЕРВУЮ ОЧЕРЕДЬ ТУТ
##Расмер картинки для распознавания. Не важно какого размера была картинка изначально, в итоге приводится к этому размеру        
frame_size = 1024
##Окно для настройки алгоритма Canny. Удобно видеть контуры обьектов
debug_window = False
##Настройки алгоритма Canny
canny_low = 25
canny_hight = 50
##Использовать или нет фильтр Калмана
use_kalman = True
##Размер зоны поиска целей. Если прицел хочет резко перескочить в другое место, это позволено только в установленных этой переменной пределах
sz = 250
##Запись отработки алгоритма в видеофайл
write_to_file = True
##Центр зоны прицеливания
targeting_x = 0
targeting_y = 0
##Размер зоны прицеливания. Если зажата кнопка мыши, то ее курсор становится центром зоны прицеливания
d_sq = 50
##Координаты центра зоны обнаружения цели
target_x = 0
target_y = 0
##Важная переменная. Если активна - лучше отслеживаются крупные цели, если неактивна - лучше для мелких целей
is_dinamic1_target_size = False
is_dinamic2_target_size = True
target_size = 100
##Максимальные размер цели, даже краем попавшей в зону обнаружения
wh_size = 250
##Минимальный размер периметра, дабы не цеплять мелкие обьекты
peri_min = 10
##Минимальное количество граней контура
approx_min = 3
#Определение по цвету
color_detection = True

##************************************************************************************************************************

##Флаг прицеливания, когда он активен обьекты находящиеся в зоне прицеливания заносятся в массив целей. Этот флаг устанавливается кликом мыши.
targeting = False
##Функция эвента, вызывается при нажатии кнопки мыши
def click(event, x, y, flags, param):
    global targeting
    global targeting_x
    global targeting_y

    if event == cv2.EVENT_LBUTTONDOWN:
        targeting = True
        targeting_x = x
        targeting_y = y
    elif event == cv2.EVENT_LBUTTONUP:
        targeting = False


##Функции фильтра Калмана
def fx(x, dt):
    # state transition function - predict next state based
    # on constant velocity model x = vt + x_0
    F = np.array([[1, dt, 0, 0],
                  [0, 1, 0, 0],
                  [0, 0, 1, dt],
                  [0, 0, 0, 1]], dtype=float)
    return np.dot(F, x)
##Функции фильтра Калмана
def hx(x):
   # measurement function - convert state into a measurement
   # where measurements are [x_pos, y_pos]
   return np.array([x[0], x[2]])


##Обьекты в которые в дальнейшем лягут два фильтра Калмана для X и Y координат цели
kfx = 0
kfy = 0

#Автоматический поиск камеры, раскоментировать при использовании камеры а не видеофайла
'''
i = 0
for i in range(10):
    cap = cv2.VideoCapture(i) #Iš kameros
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(1024))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(768))
    if cap.get(cv2.CAP_PROP_FRAME_WIDTH) > 0:
        print('selected video' + str(i))
        print(str(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),str(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        break
'''

#Видеофайлы для обработки
cap = cv2.VideoCapture('Port side drop tank  of a Tornado aircraft losing its tail section.mp4')
#cap = cv2.VideoCapture('/mnt/48ECBA7C72F0B029/Clouds Video/GH015798.MP4') #Iš video
#cap = cv2.VideoCapture("/home/ivan/Desktop/Straipsniai/Test data/ships and water/Pexels Videos 1570894.mp4") #Iš video
#cap = cv2.VideoCapture("/home/ivan/Desktop/Straipsniai/Test data/Road traffic video for object recognition.mp4") #Iš video
cap.set(cv2.CAP_PROP_FPS, 1) 

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
print(frame_width)
print(frame_height)

if write_to_file:
    writer = skvideo.io.FFmpegWriter("outputvideo.mp4")
    

##Пересчет резолюции видеокартинки
devider = frame_width/frame_size


r_frame_width = int(frame_width/devider)
r_frame_height = int(frame_height/devider)
print(r_frame_width)
print(r_frame_height)

##Для эвента клика мыши надо одинаково назвать окно вывода видео
cv2.namedWindow("Original")
cv2.setMouseCallback("Original", click)
##Массив контуров целей
t_ob_arr = []
##Бесконечный цикл в каждой итерации которого считывается по одному кадру и выполняется пересчет цели
target = 1 
counter = 0
ret = 1
while ret: 
    ##Считываем один фрэйм видео
    ##Если фрэйм получен продолжаем
    if counter == target: 
        ret, frame = cap.read() 
      # display and stuff 
        counter = 0 
    
        ##В первую очерерь меняем резолюцию фрэйма до размера по горизонтали, заданного в переменной frame_size
        frame = cv2.resize(frame, (r_frame_width, r_frame_height))
        frame_orig = frame.copy()
        ##Получаем чернобелое изображение. 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        # При помощи преобразования Канни получаем граници обектов
        edged = cv2.Canny(gray, canny_low, canny_hight)
        # Получение всех контуров фрэйма и заносим их в переменную cnts
        cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # Если контура найденны то перебираем их, проверям не дано ли новое целеуказание,
        # смотрим есть ли контуры обьектов в зоне прицеливания, помечаем контуры в зоне прицеливания, перемещаем зону прицеливания за ведомыми целями
        if cnts is not None:
            # Перебор всех конруров фрэйма
            for cn in cnts:

                #***** Для каждого контура в фрэйме получаем набор его характеристик ****
                # Длину периметра
                peri = cv2.arcLength(cn, True)
                # массив с набором граней контура
                approx = cv2.approxPolyDP(cn, 0.001 * peri, True)
                # Координаты и размеры найденного конрура                
                (x, y, w, h) = cv2.boundingRect(approx)

                crop_img = frame_orig[y:y+h, x:x+w]
                r, g, b = crop_img.mean(axis=0).mean(axis=0)

                
                # соотношение ширины к высоте контура
                aspectRatio = w / float(h)
                ##Примерные площади контура
                area = cv2.contourArea(cn)
                hullArea = cv2.contourArea(cv2.convexHull(cn))

                if hullArea > 0:
                    solidity = area / float(hullArea)
                else:
                    solidity = 0
                    
                index = 0

                # Далее перебираются все контуры помеченной цели, если цель уже была помеченна
                # Смотрим есть ли в зоне целеуказания обекты с записанными прие указании цели параметрами
                # Так как наблюдаемая цель может постоянно менятся как по размеру так и по ракурсу, находим цель по хотябы обдому признаку + по подходящим координатам
                for t_ob in t_ob_arr:
                    #поиск по цветам
                    if color_detection:
                        r_q = r <= t_ob[8] + 40 and r >= t_ob[8] - 40
                        g_q = g <= t_ob[9] + 40 and g >= t_ob[9] - 40
                        b_q = b <= t_ob[10] + 40 and b >= t_ob[10] - 40
                        colors = r_q and g_q and b_q
                    else:
                        colors = True
                    #Условия для размеров периметра контура. Если камера трясется и обьект резко меняет размеры, увеличивайте допуски периметра
                    peri_q = peri > peri_min and peri >= t_ob[0] - 10 and peri <= t_ob[0] + 50
                    #Примерное количество граней контура
                    approx_q = len(approx) > approx_min and len(approx) >= t_ob[1] - 10 and len(approx) <= t_ob[1] + 50
                    #Соотношение длины к ширине обьекта
                    aspectratio_q = aspectRatio >= t_ob[2] - 0.1 and aspectRatio <= t_ob[2] + 0.1
                    #Примерная площадь обьекта
                    area_q = area >= t_ob[3]- 10 and area <= t_ob[3] + 50
                    hullarea_q = hullArea >= t_ob[4]- 10 and hullArea <= t_ob[4] + 50
                    solidity_q = solidity >= t_ob[5] - 0.5
                    #Выбор метода задачи зоны поиска цели. Все что не входит в эту зону, перестает отслеживаться
                    if is_dinamic1_target_size:
                        x_q = x >= target_x - w  and x <= target_x + w
                        y_q = y >= target_y - h and y <= target_y  +  h
                    if is_dinamic2_target_size:
                        x_q = x >= target_x - hullArea/w  and x <= target_x +  hullArea/w
                        y_q = y >= target_y - hullArea/h and y <= target_y  +  hullArea/h
                    if is_dinamic1_target_size is False and is_dinamic2_target_size is False:
                        x_q = x >= target_x - target_size  and x <= target_x + target_size
                        y_q = y >= target_y - target_size and y <= target_y  +  target_size
                    #Основной фильтр параметров цели, хоть один из параметров должен быть истинной, иначе цель откидывается. Можно задать любую логику и любой набо параметров.
                    params =(peri_q or approx_q or aspectratio_q or area_q or hullarea_q or solidity_q)
                    #Дополнительное жесткое ограничение зоны поиска. Бывает полезно для условий со множественными целями
                    search_zone_xy = x >= target_x - sz and x <= target_x + sz and y >= target_y - sz and y <= target_y + sz
                    #Ограничение на размер обьектов, дабы не цеплять краем зоны поиска большие контуры
                    wh_zone = w < wh_size and h < wh_size                   
                    
                    #Если все условия совпали и контур в зоне обнаружения то он трактуется как цель и его параметры обновляются
                    if colors and params and (x_q and y_q) and search_zone_xy and wh_zone:
                        #Помечаем контур цели квадратом
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        #Обновляем параметры контура цели
                        t_ob_arr[index][0] = peri
                        t_ob_arr[index][1] = len(approx)
                        t_ob_arr[index][2] = aspectRatio
                        t_ob_arr[index][3] = area
                        t_ob_arr[index][4] = hullArea
                        t_ob_arr[index][5] = solidity
                        t_ob_arr[index][6] = x
                        t_ob_arr[index][7] = y
                        index += 1

                #Если были найденны контуры целей, расчитываем новые сглаженные значения зоны поиска (target_x, target_y). 
                if index > 0:
    
                    x_midle = 0
                    y_midle = 0

                    for i in range(index):
                        x_midle = t_ob_arr[i][6] + x_midle
                        y_midle = t_ob_arr[i][7] + y_midle
                    x_midle = x_midle / index
                    y_midle = y_midle / index
                    if use_kalman:
                        kfx.predict()
                        kfx.update(x_midle)
                        kfy.predict()
                        kfy.update(y_midle)
                        target_x = kfx.x[0]
                        target_y = kfy.x[0]
                    else:
                        target_x = x_midle
                        target_y = y_midle
                #Все найденные контуры на всем фрэйме очерчиваем красной кривой
                color = (0, 0, 255)
                cv2.drawContours(frame, [approx], -1, color, 1)
                                        
        #Если активен флаг прицеливания то ищем в зоне прицеливания контуры обектов и записываем параметры найденных обьектов в массив целей
        if targeting == True:
            t_ob_arr = []

            ##Создаем два фильтра Калмана для обеих координат точки прицеливания, фильтр должен пересоздаваться при каждом новом
            if use_kalman:
                dt = 0.5
                # create sigma points to use in the filter. This is standard for Gaussian processes
                points = MerweScaledSigmaPoints(4, alpha=.01, beta=2., kappa=-1)

                kfx = UnscentedKalmanFilter(dim_x=4, dim_z=2, dt=dt, fx=fx, hx=hx, points=points)
                kfy = UnscentedKalmanFilter(dim_x=4, dim_z=2, dt=dt, fx=fx, hx=hx, points=points)
                

                kfx.x = np.array([-1., 1., -1., 1]) # initial state
                kfx.P *= 0.5 # initial uncertainty
                z_std = 0.05
                kfx.R = np.diag([z_std**2, z_std**2]) # 1 standard
                kfx.Q = Q_discrete_white_noise(dim=2, dt=dt, var=0.01**2, block_size=2)


                
                kfy.x = np.array([-1., 1., -1., 1]) # initial state
                kfy.P *= 0.5 # initial uncertainty
                z_std = 0.05
                kfy.R = np.diag([z_std**2, z_std**2]) # 1 standard
                kfy.Q = Q_discrete_white_noise(dim=2, dt=dt, var=0.01**2, block_size=2)

            #Перебираем все контура в зоне прицеливания дабы занести их в массив целей
            if cnts is not None:
                for cn in cnts:

                    
                    
                    peri = cv2.arcLength(cn, True)
                    approx = cv2.approxPolyDP(cn, 0.001 * peri, True)
                    (x, y, w, h) = cv2.boundingRect(approx)
                    aspectRatio = w / float(h)


                    area = cv2.contourArea(cn)
                    hullArea = cv2.contourArea(cv2.convexHull(cn))
                    if hullArea > 0:
                        solidity = area / float(hullArea)
                    else:
                        solidity = 0

                    if peri > peri_min and len(approx) > approx_min and x > targeting_x - d_sq and x < targeting_x + d_sq and y > targeting_y - d_sq and y < targeting_y + d_sq:
                        target_x = x
                        target_y = y
                        if color_detection:
                            crop_img = frame_orig[y:y+h, x:x+w]
                            r, g, b = crop_img.mean(axis=0).mean(axis=0)
                        else:
                            r = 0
                            g = 0
                            b = 0

                        t_ob_arr.append([peri, len(approx), aspectRatio, area, hullArea, solidity, x, y, r, g, b])
                        cv2.rectangle(frame, (x - d_sq, y - d_sq), (x + d_sq, y + d_sq), (0, 255, 255), 2)
                        
      
        #Цветная картинка. По ней целимся
        cv2.imshow('Original',frame)
        
        #Черно белая картинка только с конрурами. Актуально для настройки алгоритма Canny
        if debug_window:
            cv2.imshow('edged',edged)
        
        
            
        if write_to_file:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            writer.writeFrame(frame)

        
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
    else: 
      #ret = cap.grab() 
      counter += 1 
    
if write_to_file:
    writer.close()
cv2.destroyAllWindows()
cap.release()

