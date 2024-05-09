import cv2
import numpy
import numpy as np
import PoseEstimationMin as pm
import math

cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture("bicepscurl.mp4") # videoyla beraber 88. satırdaki pose değeri de poses listesindeki hareket seçilip seğiştirilmeli


detector = pm.poseDetector()
count = 0
count_temp=0.0
dir = 0

alt_yarim=0
alt_yarim_temp=0
alt_yarim_sayac=0

ust_yarim=0
ust_yarim_temp=1
ust_yarim_sayac=0



#[[açısı ölçülecek noktalar], [ölçülecek açı aralığı], [eğer kontrol edilcekse eğim aralığı], [eğimi ölçülecek noktalar]]
poses=[
    [[11, 13, 15], [30, 165], []        , []],        # pullup
    [[12, 14, 16], [85, 155], [0.0, 0.3], [14,16]],   # dips #
    [[12, 14, 16], [60, 150], [0.7, 0.9], [12,24]],   # triceps pushdown
    [[11, 13, 15], [60, 170], [6  ,  13], [23,11]],   # bench press
    [[15, 13, 11], [50, 150], []        , []],        # biceps curl
    [[11, 13, 15], [90, 155], [0.05,0.2], [13,15]],   # dumbell shoulder press
    [[13, 11, 23], [40, 90 ], []        , []],        # dumbell lateral raise
    [[23, 25, 27], [70, 150], []        , []],        # leg extension
    [[23, 25, 27], [90, 160], []        , []],        # seated leg curl
    [[24, 26, 28], [170,270], []        , []],        # leg press
    [[12, 14, 16], [50, 180], [3, 10]   , [14,12]],   # dumbbell kickback
]





def estimation(img,pose):
    angle = detector.findAngle(img, poses[pose][0][:]) # istediğimiz 3 nokta arasındaki açıyı aldık
    per = np.interp(angle, (poses[pose][1][0], poses[pose][1][1]), (0, 100)) # yukarıda listede geçerli açı aralığını yüzdelik dilime çevirdik

    per=egim_hesapla(pose,per)

    if pose==3 and angle> 300: # bench press için fazla aşağı indirince 360 a atlıyor. bu da 170 ten büyük olunca 2 sayıyor. o yüzden bu durumdada per değerini 0 yapıyoruz.
        per = 0

    return per


def egim_hesapla(pose,per):
    if poses[pose][3] != []: # eğim girdisi varsa çalışır. iki nokta arasınaki eğimi hesaplar
        id, x1, y1 = lmList[poses[pose][3][0]] # birinci noktanin koordinatlari
        id, x2, y2 = lmList[poses[pose][3][1]] # ikinci noktanin koordinatlari
        m = numpy.absolute((x1 - x2)) / numpy.absolute((y2 - y1))  # eğim
        cv2.putText(img, f'{m:.1f}', (150, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    else:
        m=0 # eğer eğim kontrolü yapılmayacaksa eğim direkt 0 olarak belirleniyor

    if poses[pose][2] != []: # eğim değerlerinin kontrolü. istediğimiz eğim değerleri arasında değilse saymaz
        if m < poses[pose][2][0] or m > poses[pose][2][1]: # eğer istenilen değerler içerisinde değilse saymaması için per = 0 yapıyoruz
            cv2.circle(img,(600, 50),20,(0, 0, 255),-1) # istenilen eğim içerisinde değilse kamera versinin sağ üstüne kırmızı daire çiziyor
            per = 0
            return per

    return per



while True:
    success, img = cap.read() # görüntüyü yakalama işlemi
    img = detector.findPose(img) # eklemler arasındaki çizgileri çizen metod
    lmList = detector.findPosition(img, draw=False) # eklemleri nokta ile işaretleyen ve eklemlerin id ve kooordinatlarını dönen metod
    pose = 4 # yukarıdaki listeden hangi hareket hareketi yapacaksak onu seçiyoruz


    if len(lmList) != 0 : # eklem noktalari tespit edildi mi
        per= estimation(img, pose)
        alt_yarim=0
        ust_yarim=0

        # sayma
        if per == 100: # kol tamamen aşağı indiğinde
            alt_yarim = 1
            if dir == 0:
                count += 0.5
                dir = 1


        if per == 0: # kol tamamen yukarı çıktığında
            ust_yarim = 1
            if dir == 1:
                count += 0.5
                dir = 0

        cv2.putText(img, f'{int(count)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)
        cv2.putText(img, f'{int(per)}', (180, 150), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)


    # yarım hareketleri sayma kısmı
    if alt_yarim_temp!=alt_yarim:
        alt_yarim_sayac += 1
        alt_yarim_temp=alt_yarim

    if ust_yarim_temp != ust_yarim:
        ust_yarim_sayac += 1
        ust_yarim_temp = ust_yarim

    if count_temp != count:  # eğer hareket tamsa yarım 1 eksiltiyor. çünkü yarım değerler tam sayılırken de artıyor. tam hareketi 2 yarım hareket oluşturduğu için tam sayılırken de yarımlar artıyor. bu yüzden tam sayılınca yarım hareket 1 eksiltiliyor.
        alt_yarim_sayac -= 1
        ust_yarim_sayac -= 1

    yarim_hareket = (alt_yarim_sayac+ust_yarim_sayac) / 2


    cv2.putText(img, f'{int(math.floor(yarim_hareket))}', (50, 150), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)


    count_temp=count
    cv2.imshow("Image", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):

        toplam_hareket = count + yarim_hareket
        dogru_hareket_orani = (count/toplam_hareket)*100
        print('Toplam yapılan tekrar sayısı: ',toplam_hareket,'\nDoğru yapılan tekrar sayısı: ',count,'\nYarım yapılan tekrar sayısı: ',yarim_hareket)
        print('Doğru yapılan hareket yüzdesi: ',dogru_hareket_orani)
        print(dogru_hareket_orani)
        break

cv2.destroyAllWindows()