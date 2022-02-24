import cv2
import numpy as np
import threading
#from pyOpenBCI import OpenBCICyton
import csv
import argparse
import os
import glob
import time
from matplotlib import pyplot as plt
import socket
import json

SCALE_FACTOR = (4500000)/24/(2**23-1) #From the pyOpenBCI repo
playvid = False
hand = "idle"
light_show = True
data = np.zeros((1,19)).tolist()

def main():
    global playvid
    global light_show
    global data
    global hand


    # Initialize plot.
    fig, ax = plt.subplots()

    # Initialize plot line object(s). Turn on interactive plotting and show plot.
    lw = 3
    alpha = 0.5
    # data_p = np.array(data.copy())
    # pl, = ax.plot(data_p[:,-3])
    # plt.ion()
    # plt.show()


    width = args.width
    height = args.height
    fps = 30

    frameref_ms = int(time.time()*1000)
    frametime_ms = int(1000/fps)

    plane = np.zeros((width,height,3))

    #cv2.imwrite('plane.png',plane)

    menu_plane = cv2.imread('resource/menu.jpg')
    menu_plane = cv2.resize(menu_plane,(width,height))
    cv2.putText(menu_plane, f'user : {args.user}'
                , (20,20), cv2.FONT_HERSHEY_SIMPLEX, 1, [255, 255, 255], 2)

    open_left = cv2.imread('resource/open_hand_left.jpg')
    open_left = cv2.resize(open_left,(width,height))

    open_right = cv2.imread('resource/open_hand_right.jpg')
    open_right = cv2.resize(open_right,(width,height))

    open_both = cv2.imread('resource/open_hand_both.jpg')
    open_both = cv2.resize(open_both,(width,height))

    close_left = cv2.imread('resource/close_hand_left.jpg')
    close_left = cv2.resize(close_left,(width,height))

    close_right = cv2.imread('resource/close_hand_right.jpg')
    close_right = cv2.resize(close_right,(width,height))

    close_both = cv2.imread('resource/close_hand_both.jpg')
    close_both = cv2.resize(close_both,(width,height))

    # prepare_left = cv2.imread('resource/prepare_hand_left.png')
    # prepare_left = cv2.resize(prepare_left,(width,height))

    # prepare_right = cv2.imread('resource/prepare_hand_right.png')
    # prepare_right = cv2.resize(prepare_right,(width,height))

    # prepare_both = cv2.imread('resource/prepare_hand_both.png')
    # prepare_both = cv2.resize(prepare_both,(width,height))

    up_foot = cv2.imread('resource/up_foot.jpg')
    up_foot = cv2.resize(up_foot,(width,height))

    down_foot = cv2.imread('resource/down_foot.jpg')
    down_foot = cv2.resize(down_foot,(width,height))

    # prepare_foot = cv2.imread('resource/prepare_foot.png')
    # prepare_foot = cv2.resize(prepare_foot,(width,height))

    rest_frame = cv2.imread('resource/rest.jpg')
    rest_frame = cv2.resize(rest_frame,(width,height))

    blank_frame = cv2.imread('resource/blank.jpg')
    blank_frame = cv2.imread('resource/blank.jpg')

    open_frame = {"left":open_left, "right":open_right, "both":open_both, "foot":up_foot}
    close_frame = {"left":close_left, "right":close_right, "both":close_both, "foot":down_foot}

    ret = True
    playvid = False
    light_show = False
    counter = 0
    status = "rest"


    process_time = 0

    while True:
        frameref_ms += frametime_ms
        if playvid:
            for task in ['left','right','both','foot']:
                counter = 0
                for n_l in range(args.largeloop):
                    for counter in range(fps*22):
                        tic = time.time()
                        if counter < fps*3: #rest
                            status = "rest"
                            show_frame = rest_frame
                        elif fps*3 <= counter < fps*4.5: #en
                            status = task
                            light_show = True
                            show_frame = close_frame[task]

                        elif fps*4.5 <= counter < fps*6: #dis
                            status = task
                            light_show = False
                            show_frame = open_frame[task]
                        elif fps*6 <= counter < fps*7.5: #en
                            status = task
                            light_show = True
                            show_frame = close_frame[task]
                        elif fps*7.5 <= counter < fps*9: #dis
                            status = task
                            light_show = False
                            show_frame = open_frame[task]
                        elif fps*9 <= counter < fps*12: #rest
                            status = "rest"
                            light_show = False
                            show_frame = rest_frame
                        
                        if counter == (fps*12):
                            save_no = len(glob.glob(f"bci_data/{args.user}/{args.user}_{task}*.csv"))
                            print(f"bci_data/{args.user}/{args.user}_{task}_{save_no}.csv")
                            data_save(f"bci_data/{args.user}/{args.user}_{task}_{save_no}.csv")
                            data = []
                        if fps*12 <= counter  < fps*22:
                            status = "break"
                            light_show = False
                            show_frame = blank_frame
                        elif counter >= fps*22:
                            save_no = len(glob.glob(f"bci_data/{args.user}/{args.user}_break*.csv"))
                            print(f"bci_data/{args.user}/{args.user}_break_{save_no}.csv")
                            data_save(f"bci_data/{args.user}/{args.user}_break_{save_no}.csv")
                            data = []
                        toc = time.time()
                        process_time = toc - tic
                        cv2.imshow('frame', show_frame)
                        #print(process_time)
                        k2 = cv2.waitKey(int(1000/fps - process_time*1000)) & 0xFF

                

        else:
            cv2.imshow('frame',menu_plane)
            process_time = 0
        #playvid=False

        k = cv2.waitKey(int(1000/fps - process_time*1000)) & 0xFF
        if k == 27 or k==ord('q'):
            if playvid == True:
                print("Please stop video before quit")
            else:
                break
        
        elif k == ord('s'):
            if playvid==False:
                playvid=True
                counter = 0
                data = []
            else:
                print("Loop is running")

def save_data(sample):
    global data
    global hand
    global light_show
    data.append([i*SCALE_FACTOR for i in sample.channels_data] + [hand, light_show, time.time()])

def start_board():
    global data
    global hand
    global light_show
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (args.ip, args.port)
    sock.bind(server_address)
    while True:
        sub_data, addr = sock.recvfrom(20000)
        sub_data = json.loads(sub_data.decode())['data']
        data.append(sub_data + [hand, light_show, time.time()])
        #print(sub_data)

class data_thread(threading.Thread):
    def __init__(self,event):
        threading.Thread.__init__(self)
        self.stopped = event
        global data
        global hand
        global light_show
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (args.ip, args.port)
        sock.bind(server_address)
        self.sock = sock
    
    def run(self):
        global data
        global hand
        global light_show
        while not self.stopped.wait(1/500):
            sub_data, addr = self.sock.recvfrom(20000)
            sub_data = json.loads(sub_data.decode())['data']
            data.append(sub_data + [hand, light_show, time.time()])


def data_save(save_name):
    global data
    #print(data)
    with open(save_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    

parser = argparse.ArgumentParser()
parser.add_argument('-u','--user',required=True,type=str)
#parser.add_argument('-p','--port',default='/dev/tty.usbserial-DM02590B',type=str)
parser.add_argument('-n','--nloop',default=3,type=int)
parser.add_argument('-l','--largeloop',default=10,type=int)
parser.add_argument('--width',default=1920,type=int)
parser.add_argument('--height',default=1080,type=int)
parser.add_argument("--ip",default="127.0.0.1", help="The ip to listen on")
parser.add_argument("-p","--port",type=int, default=12345, help="The port to listen on")
parser.add_argument("--address",default="/openbci", help="address to listen to")
parser.add_argument("--option",default="print",help="Debugger option")
parser.add_argument("--len",default=8,help="Debugger option")

args = parser.parse_args()


if __name__ == '__main__':
    if not os.path.isdir('bci_data'):
        os.makedirs('bci_data')
    if not os.path.isdir(f'bci_data/{args.user}'):
        os.makedirs(f'bci_data/{args.user}')

    stopFlag = threading.Event()
    thread = data_thread(stopFlag)
    thread.start()

    # x = threading.Thread(target=start_board)
    # x.daemon = True
    # x.start()
    main()
    stopFlag.set()