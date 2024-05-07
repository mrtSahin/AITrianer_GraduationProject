import cv2
import numpy
import numpy as np
import PoseEstimationMin as pm

#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("bicepscurl.mp4") # videoyla beraber 88. satırdaki pose değeri de poses listesindeki hareket seçilip seğiştirilmeli


detector = pm.poseDetector()
count = 0
count_temp=0.0
dir = 0
maxM = 0

alt_yarim=0
alt_yarim_temp=0
alt_yarim_sayac=0

ust_yarim=0
ust_yarim_temp=0
ust_yarim_sayac=0






#[[açısı ölçülecek noktalar], [ölçülecek açı aralığı], [eğer kontrol edilcekse eğim aralığı], [eğimi ölçülecek noktalar]]
poses=[
    [[11, 13, 15], [30, 165], [],[]], # pullup
    [[12, 14, 16], [85, 155], [0.0,0.3], [14,16]], # dips #
    [[12, 14, 16], [60, 150], [0.7,0.9], [12,24]], # triceps pushdown
    [[11, 13, 15], [60, 170], [6  , 13], [23,11]], # bench press
    [[15, 13, 11], [50, 150], [], []], # biceps curl
    [[11, 13, 15], [90, 155], [0.05,0.2], [13,15]], # dumbell shoulder press
    [[13, 11, 23], [40, 90], [], []], # dumbell lateral raise
    [[23, 25, 27], [70, 150], [], []], # leg extension
    [[23, 25, 27], [90, 160], [], []], # seated leg curl
    [[24, 26, 28], [170, 270], [], []], # leg press
    [[12, 14, 16], [50, 180], [3,10], [14,12]], # dumbbell kickback
]

# HAREKETİN DOĞRUSUNU VİDEO ÜZERİNE EKLEME





def estimation(img,lmList,maxM,pose):
    #print('Pose Estimation')
    #print(poses[pose][1][0])

    angle = detector.findAngle(img, poses[pose][0][:]) # istediğimiz 3 nokta arasındaki açıyı aldık
    per = np.interp(angle, (poses[pose][1][0], poses[pose][1][1]), (0, 100)) # yukarıda listede geçerli açı aralığını yüzdelik dilime çevirdik


    if poses[pose][3] != []: # eğim girdisi varsa çalışır. iki nokta arasınaki eğimi hesaplar
        id, x1, y1 = lmList[poses[pose][3][0]]
        #print(x1,y1)
        id, x2, y2 = lmList[poses[pose][3][1]]
        #print(x2, y2)
        m = numpy.absolute((x1 - x2)) / numpy.absolute((y2 - y1))  # eğim
        #print('m', m)

        if maxM < m:
            maxM = m
        #print('maxM', maxM, '\n-------------')



    if poses[pose][2] != []: # eğim değerlerinin kontrolü. istediğimiz eğim değerleri arasında değilse saymaz
        if maxM < poses[pose][2][0] or maxM > poses[pose][2][1]: # eğer istenilen değerler içerisinde değilse saymaması için per = 0 yapıyoruz
            print("sayılmadı///////////////////////////////////////////////////////////////////")
            per = 0
            maxM = 0



    if pose==3 and angle> 300: # bench press için fazla aşağı indirince 360 a atlıyor. bu da 170 ten büyük olunca 2 sayıyor. o yüzden bu durumdada per değerini 0 yapıyoruz.
        per = 0


    return per, float(maxM)

while True:
    success, img = cap.read()
    img = detector.findPose(img)
    lmList = detector.findPosition(img, draw=False)
    pose = 4




    if len(lmList) != 0 :
        per, maxM = estimation(img, lmList, maxM, pose)
        alt_yarim=0
        ust_yarim=0

        # sayma
        if per == 100:
            alt_yarim = 1
            if dir == 0:
                count += 0.5
                dir = 1


        if per == 0:
            ust_yarim = 1
            if dir == 1:
                count += 0.5
                dir = 0



        #print(count)


        cv2.putText(img, f'{int(count)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)
        cv2.putText(img, f'{maxM:.1f}', (150, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        cv2.putText(img, f'{int(per)}', (180, 150), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)

        if count_temp != count: # eğer hareket tamsa yarım değerleri sıfırlıyor
            ust_yarim_sayac = 0
            alt_yarim_sayac = 0


    if alt_yarim_temp!=alt_yarim:
        alt_yarim_sayac+=0.5

        alt_yarim_temp=alt_yarim

    if ust_yarim_temp != ust_yarim:
        ust_yarim_sayac += 0.5

        ust_yarim_temp = ust_yarim

    print(count_temp)



    print("ALT yarim yaptı",f'{int(alt_yarim_sayac)}')
    print("------------------ÜST yarim yaptı", f'{int(ust_yarim_sayac)}')

    count_temp=count
    #cTime = time.time()
    #fps = 1 / (cTime - pTime)
    #pTime = cTime

    #cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    #print("alt yarım", alt_yarim_sayac, int(alt_yarim_sayac))
    #print("üst yarım", ust_yarim_sayac)
    #print("yarım yapılan hareket sayısı: ", int(alt_yarim_sayac) + int(ust_yarim_sayac) - int(count)*2 )




    cv2.imshow("Image", img)
    cv2.waitKey(1)

