import cv2
import numpy as np
import argparse
import os
import socket
import time

parser = argparse.ArgumentParser(description='realtime drone detect')
parser.add_argument('--camera', type=int, default=0)
parser.add_argument('--videourl', type=str, default=None, help='capture from video url (udp:// etc)')
parser.add_argument('--id', type=str, default="0", help='set coord')
parser.add_argument('--coord', type=str, default="x", help='set coord')
parser.add_argument('--ip', type=str, default="192.168.0.28", help='set ip')
parser.add_argument('--port', type=int, default=12345, help='set port')
parser.add_argument('--vstart', type=int, default=-1, help='skip first n frames')
parser.add_argument('--pos', help='calc position', action='store_true')
parser.add_argument('--dbgpos', help='calc position with debug pos', action='store_true')
parser.add_argument('--pre', help='enable pre process', action='store_true')
parser.add_argument('--image', help='Enable image input', action='store_true')
parser.add_argument('--min', help='resize to 640x360', action='store_true')
parser.add_argument('--raw', help='show rawcolor', action='store_true')
parser.add_argument('--nosend', help='disable socket', action='store_true')
parser.add_argument('--rev', help='reverse pos', action='store_true')
parser.add_argument('--depth', help='', action='store_true')
args = parser.parse_args()

C_BLUE = 0
C_GREEN = 1
C_RED = 2
C_PURPLE = 3
COL_NAME = ["BLUE", "GREEN", "RED", "PURPLE"]

HOST = args.ip
PORT = args.port
if not args.nosend:
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def preproc(img):
    # https://imagingsolution.net/program/python/opencv-python/opencv-reference/opencv-python-gaussianblur/
    r = cv2.GaussianBlur(img, (9,9),0)
    # https://www.codevace.com/py-opencv-contrast-and-brightness/
    # r = cv2.convertScaleAbs(r, alpha=1, beta=0)
    return r

def calcpos(img, mask):
    # https://imagingsolution.net/program/python/opencv-python/opencv-python-findcontours/
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    alla = img.shape[0] * img.shape[1]
    fst = True
    for cn in contours:
        gx , gy = 0 , 0
        for pos in cn:
            gx += pos[0][0]
            gy += pos[0][1]
        # gx,gy: 検知した位置(重心)
        gx //= len(cn)
        gy //= len(cn)
        area = cv2.contourArea(cn) / alla
        if area < 0.0001 : continue
        
        if fst and args.dbgpos:
            rendpos(img,gx, gy, (0, 255, 255))
            cv2.putText(img, f"area: {area:.7f}", (10, 21), thickness=2, fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=(0, 255, 255), fontScale=0.8)
            
        fst = False
        # areaに対する閾値で抑制できるかも？
        if area < 0.0002 or area > 0.25 : continue
        nx = gx / img.shape[1]
        ny = 1 - (gy/img.shape[0]) # 下が0, 上が1
        return (True, gx, gy, nx, ny)
    return (False, 0, 0, 0, 0)

def rendpos(img, px, py, col=(0,0,255)):
    cv2.rectangle(img,(px - 8, py - 8), (px + 8, py + 8), col, thickness=2)
    
        

#https://craft-gogo.com/python-opencv-color-detection/
#https://www.peko-step.com/html/hsv.html
def get_mask(hsv, cid):
    if C_BLUE == cid:
        lower = np.array([95,110,80])    #変更点
        upper = np.array([126,255,255]) #変更点
        frame_mask = cv2.inRange(hsv, lower, upper)
    elif C_GREEN == cid:
        lower = np.array([69,30,32])
        upper = np.array([84,255,255])
        frame_mask = cv2.inRange(hsv, lower, upper)
    elif C_PURPLE == cid:
        lower = np.array([130,32,0])
        upper = np.array([140,192,255])
        frame_mask = cv2.inRange(hsv, lower, upper)
    elif C_RED == cid:
        lower = np.array([0,96,120])
        upper = np.array([4,255,255])
        frame_mask1 = cv2.inRange(hsv, lower, upper)

        lower = np.array([176,96,120])
        upper = np.array([180,255,255])

        frame_mask2 = cv2.inRange(hsv, lower, upper)
        frame_mask = frame_mask1 + frame_mask2
    return frame_mask

def depth_modify(c):
    m = 1 # メートル
    return c / (0.2*m)
        
    

if args.videourl is None:
    cam = cv2.VideoCapture(args.camera)
else:
    cam = cv2.VideoCapture(args.videourl)
    if args.image:
        _, dat = cam.read()
    if args.vstart > 0:
        cam.set(cv2.CAP_PROP_POS_FRAMES, args.vstart)



while True:
    #画像データの読み込み
    if args.image:
        img = dat
    else:
        ret_val, img = cam.read()
        if not ret_val:
            time.sleep(1e-4)
            continue
    if args.min:
        img = cv2.resize(img, (640, 360))
    if args.pre:
        img = preproc(img)
    #BGR色空間からHSV色空間への変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    poses = {}
    for char in args.coord:
        poses[char] = []

    for i in range(3):
        mask = get_mask(hsv, i)
        if args.raw:
            dst = cv2.bitwise_and(img, img, mask=mask)
        else:
            dst = cv2.bitwise_and(hsv, hsv, mask=mask)
        if args.pos or args.dbgpos:
            ret, x, y, nx, ny = calcpos(dst, mask)
            if ret:
                if args.rev:
                    nx = 1 - nx
                for char in args.coord:
                    if args.depth:
                        ny = depth_modify(ny)
                    if char in "xy":
                        poses[char].append((i, nx))
                    elif char in "z":
                        poses[char].append((i, ny))
                rendpos(dst, x,y)
            
        cv2.imshow("image " + COL_NAME[i], dst)
    
    if len(poses[args.coord[0]]) > 0:
        for k, v in poses.items():
            st = f"{k}"+ "".join([f"({id},{round(c, 4)})" for id, c in v])
            if not args.nosend:
                message = f'coord:{args.id}:{st}'
                soc.sendto(message.encode(), (HOST, PORT))
    if args.raw:
        cv2.imshow("image raw" , img)
    else:
        cv2.imshow("image raw" , hsv)
    
    if cv2.waitKey(1) == 27:
      break


cv2.destroyAllWindows()