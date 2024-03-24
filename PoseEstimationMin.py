import cv2
import mediapipe as mp
import math



class poseDetector():
    def __init__(self):
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose =  self.mpPose.Pose()


    def findPose(self, img, draw = True): # noktaları tespit edip çizen metod
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB) # opencv görüntüyü ilk başta bgr olarak tespit eder. Görüntüyü bizim anlayabileceğimiz renk skalasına getirmek için bu işlemi yapıp rgb e çeviririz.
        self.results = self.pose.process(imgRGB) # Bir RGB görüntüsünü işler ve tespit edilen en belirgin kişinin poz yer işaretlerini(eklem nokktaları) döndürür.
        # Poz yer işaretlerini içeren pose_landmarks" alanıdır. Burası eklem noktalarıdır.

        if self.results.pose_landmarks: # eğer eklem noktaları tespit edildiyse görüntü üzerinde çizim yapar.
            if draw:
                self.mpDraw.draw_landmarks(img,self.results.pose_landmarks,self.mpPose.POSE_CONNECTIONS) # GÖRÜNTÜDE NOKTALARI İŞARETLER VE BAĞLANTILARI ÇİZER.
        return img

        #for id,lm in enumerate(results.pose_landmarks.landmark):
            #h, w, c= img.shape
            #print(id,lm)
            #cx,cy=int(lm.x*w) , int(lm.y*h)
            #cv2.circle(img, (cx,cy), 5, (255,0,0), cv2.FILLED)

    def findPosition(self, img, draw=True): # tespit edilen noktaların id ve x-y konumlarını veren metod. ve bunları işaretleyen metod.
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark): # tespit edilen noktaların bilgilerinin tutulduğu listede for ile dolanıyoruz.
                h, w, c = img.shape # resmin yükselik ve genişlik değerini aldık
                #print(id, lm)
                cx, cy = int(lm.x * w), int(lm.y * h) # noktaların tam konumlarını almak için bu işlem yapılıyor. landmark bize tam konum vermiyor.
                self.lmList.append([id, cx, cy]) # tespit edilen noktaların id ve x-y konumlarını
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 255, 0), cv2.FILLED) # GÖRÜNTÜDE SADECE NOKTLARI İŞARETLER
        return self.lmList

    def findAngle(self, img, dots, draw=True): # bizim belirlediğimiz 3 nokta arasındaki açıyı hesaplayıp bu noktaları belirtecek şekilde çizen metod.
        # dots değişkeni içerisinde noktaların id bilgisi tutulur.

        angle = 0

            # Noktaların konum bilgileri alınır
        x1, y1 = self.lmList[dots[0]][1:]
        x2, y2 = self.lmList[dots[1]][1:]
        x3, y3 = self.lmList[dots[2]][1:]

        # Calculate the Angle
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        # atan2 metodu hayali 360 derece grafikte, belirli iki nokta arasındaki tanjantı ranyan cinsinden verir.
        # degrees metodu radyanı dereceye çevirir.

        if angle < 0: # açı ters olunca yanlış açı bilgisi vermemesi için bu işlem yapılır.
            angle += 360

        # print(angle)

        # Draw
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 0, 255), 2)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 0, 255), 2)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        return angle


