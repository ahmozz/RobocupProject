import struct
from random import randint

def http_control(content):
    header=(b'POST /scan HTTP/1.1\r\n'+
            b'Host: %s:%d\r\n'+
            b'Content-Type: text/plain\r\n'+
            b'Content-Length: %d\r\n'+
            b'Connection: keep-alive\r\n'+
            b'\r\n')%(IP_RASP_PORT, HTTP_PORT, len(content))

    # print(sys.getsizeof(content))
    print("+++++++++++++++++++")
    stream.write(header)
    stream.write(content)
    stream.flush()
    (status, conn, length)=(b'', b'', b'')
    while True:
        print("************1")
        #l=stream.readline()
        l=None
        # print("l after write is : ", l)
        # sys.stderr.write('%s\n'%l)
        print("******************11")
        if not l or l==b'\r\n' or l==b'\n':
            break
        if not status: # first line
            (version, status)=l.split()[0:2]
        elif l.startswith(b'Content-Length:'):
            length=l.split(None, 1)[1].strip()

        print("************2")
    if status!=b'200' or not length: return None
    length=int(length) if length else 0
    reply=b''
    while length:
        r=stream.read(length)
        if not r: break
        reply+=r
        length-=len(r)
        print("************3")
    return reply


#**import numpy as np
#**import cv2
#**import cv2.aruco as aruco
import socket
import sys
import json

#**cap = cv2.VideoCapture(0)

# For http connexion :
IP_RASP_PORT = b"localhost"#b'10.3.141.1' # IP of the Raspberry by WIFI
HTTP_PORT = 8051
print("HTTP target port:", IP_RASP_PORT)

# Test of HTTP functionnalities
client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
client_socket.connect((IP_RASP_PORT, HTTP_PORT))
stream=client_socket.makefile('rwb')

k = 0
while(True):
    # Capture frame-by-frame
    #**ret, frame = cap.read()
    #print(frame.shape) #480x640
    # Our operations on the frame come here

    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    #parameters =  aruco.DetectorParameters_create()

    #print(parameters)

    '''    detectMarkers(...)
        detectMarkers(image, dictionary[, corners[, ids[, parameters[, rejectedI
        mgPoints]]]]) -> corners, ids, rejectedImgPoints
        '''
    #lists of ids and the corners beloning to each idq
    #corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    print("************IDS")
    #print(ids)
    print("************CORNERS")

    corners_b = []
    all_corners = []
    buff = None

    #for corners_br in corners:

    #    corners_byrobot = []
    #    for corner in corners_br:

    #        for absc in corner:
    #            print(absc)
    #            print("++")
    #            point = [int(absc[0]), int(absc[1])]
    #            corners_byrobot.extend(point)
    #            print(point)

    #    all_corners.extend(corners_byrobot)

    #buff = struct.pack('B' * len(all_corners), *all_corners)
    #all_corners = [1, 251, 256, 350, 4, 154, 250, 250]
    all_corners = [
        randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360),
        randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360),
        randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360), randint(0,360)
    ]
    #all_corners = [150,150,150,150,150,150,150,150]

    if len(all_corners) % 4 != 0:
        print('ERROR!!!!!!')
        print('CORNERS NUMBERS IS NOT DIVISABLE')
        pass

    data = []
    nbrRobots = int(len(all_corners) / 8)
    print(nbrRobots)

    for i in range(1, nbrRobots+1):
        print('|||||||||||||||||||')
        robot = {}
        robot['id'] = i

        robot['corner1'] = {'x': all_corners[i-1], 'y': all_corners[i]}
        robot['corner2'] = {'x': all_corners[i+1], 'y': all_corners[i+2]}
        robot['corner3'] = {'x': all_corners[i+3], 'y': all_corners[i+4]}
        robot['corner4'] = {'x': all_corners[i+5], 'y': all_corners[i+6]}

        data.append(robot)


    json_by = json.dumps(data, separators=(',', ':')).encode('utf-8')

    buff = struct.pack('f' * len(all_corners), *all_corners)

    print('#########################*')
    print(json_by)
    print('#########################')
    #print(json_data)
    #print(len(json_data))
    print('#########################')
    #print(jsona)
    print('#########################')
    #print(type(jsona))
    #print(all_corners)

    # print(sys.getsizeof(ids))
    # print("************")

    #It's working.
    # my problem was that the cellphone put black all around it. The alrogithm
    # depends very much upon finding rectangular black blobs

    #gray = aruco.drawDetectedMarkers(gray, corners)
    k+=1
    if all_corners is not None and k>500:
        http_control(json_by)
        k=0

    #print(rejectedImgPoints)
    # Display the resulting frame
    #cv2.imshow('frame',gray)
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
