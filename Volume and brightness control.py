import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, pointer
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc

wCam, hCam = 640, 480
detector = htm.handDetector(detectionCon=0.8)
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
cTime = 0
pTime = 0

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 370

while True:
    succuss, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        x3, y3 = lmList[12][1], lmList[12][2]
        cx1, cy1 = ((x1 + x2) // 2), ((y1 + y2) // 2)
        cx2, cy2 = ((x1 + x3) // 2), ((y1 + y3) // 2)

        cv2.circle(img, (x1, y1), 10, (237, 149, 100), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (237, 149, 100), cv2.FILLED)
        cv2.circle(img, (cx1, cy1), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (cx2, cy2), 10, (255, 255, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
        cv2.line(img, (x1, y1), (x3, y3), (255, 255, 255), 3)

        length1 = math.hypot(x2 - x1, y2 - y1)
        length2 = math.hypot(x3 - x1, y3 - y1)
        print(length1, length2)


        # Hand Range 20 - 150
        # Volume range -65 - 0

        vol = np.interp(length1, [20, 150], [minVol, maxVol])
        volBar = np.interp(length1, [20, 150], [370, 120])
        volper = np.interp(length1, [20, 150], [0, 100])
        bright = np.interp(length2, [20, 150], [0, 100])


        volume.SetMasterVolumeLevel(vol, None)
        sbc.set_brightness(bright)



        if length1 < 20:
            cv2.circle(img, (cx1, cy1), 10, (0, 0, 0), cv2.FILLED)

        if length1 > 150:
            cv2.circle(img, (cx1, cy1), 10, (0, 0, 255), cv2.FILLED)

        if length2 < 20:
            cv2.circle(img, (cx2, cy2), 10, (0, 0, 0), cv2.FILLED)

        if length2 > 150:
            cv2.circle(img, (cx2, cy2), 10, (0, 0, 255), cv2.FILLED)

        cv2.rectangle(img, (20, 120), (55, 370), (185, 128, 41), 2) # volume
        # cv2.rectangle(img, (596, 120), (620, 370), (185, 128, 41), 2)
        cv2.rectangle(img, (20 ,int(volBar)),(55, 370), (255,255,255), -1)# volume
        # cv2.rectangle(img, (596,int(bright)),(620, 370 ), (255,255,255), -1)
        cv2.putText(img, f'{int(volper)}%', (21, 250), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 0, 0), 1)# volume
        # cv2.putText(img, f'{int(bright)}%', (598, 619 ), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 0, 0), 1)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS:{int(fps)}', (10, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Img", img)
    cv2.waitKey(1)
