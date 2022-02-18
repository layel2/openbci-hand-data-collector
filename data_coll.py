from turtle import down
import cv2
import numpy as np
import threading
from pyOpenBCI import OpenBCICyton
import csv
import argparse
import os
import glob
import time
from matplotlib import pyplot as plt

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


    width = 800
    height = 800
    fps = 30

    frameref_ms = int(time.time()*1000)
    frametime_ms = int(1000/fps)

    plane = np.zeros((width,height,3))

    #cv2.imwrite('plane.png',plane)

    menu_plane = cv2.imread('resource/menu.png')
    menu_plane = cv2.resize(menu_plane,(width,height))
    cv2.putText(menu_plane, f'user : {args.user}'
                , (20,20), cv2.FONT_HERSHEY_SIMPLEX, 1, [255, 255, 255], 2)

    open_left = cv2.imread('resource/open_hand_left.png')
    open_left = cv2.resize(open_left,(width,height))

    open_right = cv2.imread('resource/open_hand_right.png')
    open_right = cv2.resize(open_right,(width,height))

    open_both = cv2.imread('resource/open_hand_both.png')
    open_both = cv2.resize(open_both,(width,height))

    close_left = cv2.imread('resource/close_hand_left.png')
    close_left = cv2.resize(close_left,(width,height))

    close_right = cv2.imread('resource/close_hand_right.png')
    close_right = cv2.resize(close_right,(width,height))

    close_both = cv2.imread('resource/close_hand_both.png')
    close_both = cv2.resize(close_both,(width,height))

    prepare_left = cv2.imread('resource/prepare_hand_left.png')
    prepare_left = cv2.resize(prepare_left,(width,height))

    prepare_right = cv2.imread('resource/prepare_hand_right.png')
    prepare_right = cv2.resize(prepare_right,(width,height))

    prepare_both = cv2.imread('resource/prepare_hand_both.png')
    prepare_both = cv2.resize(prepare_both,(width,height))

    up_foot = cv2.imread('resource/up_foot.png')
    up_foot = cv2.resize(up_foot,(width,height))

    down_foot = cv2.imread('resource/down_foot.png')
    down_foot = cv2.resize(down_foot,(width,height))

    prepare_foot = cv2.imread('resource/prepare_foot.png')
    prepare_foot = cv2.resize(prepare_foot,(width,height))

    ret = True
    playvid = False
    light_show = False
    counter = 0

    process_time = 0

    while True:
        frameref_ms += frametime_ms
        #print(counter, time.time())
        if playvid and ret:
            tic = time.time()
            if counter < fps*3:
                cv2.imshow('frame',prepare_frame)
            
            elif counter >= fps*3:
                if (counter % fps) == 0:
                    light_show = not light_show
                if light_show:
                    cv2.imshow('frame',close_frame)
                else:
                    cv2.imshow('frame',open_frame)
            if counter == 90 + (args.nloop * 2 * fps):
                print('Done')
                playvid = False
                save_no = len(glob.glob(f"bci_data/{args.user}/{args.user}_{hand}*.csv"))
                print(f"bci_data/{args.user}/{args.user}_{hand}_{save_no}.csv")
                data_save(f"bci_data/{args.user}/{args.user}_{hand}_{save_no}.csv")
                data = []
                hand = 'idle'
                continue
            counter += 1
            toc = time.time()
            process_time = toc - tic
            # ret,frame = vid.read()
            # if not ret:
            #     playvid = False
            #     continue
            # frame = cv2.resize(frame,(plane.shape[0],plane.shape[1]))
        else:
            cv2.imshow('frame',menu_plane)
            process_time = 0
        #print(process_time)
        #data_p = np.array(data.copy())
        #print(data_p.shape)
        #pl.set_ydata(np.arange(len(data_p)))
        # try :
        #     pl.set_xdata(np.arange(len(data_p)))
        #     pl.set_ydata(data_p[:,0].astype(float))
        #     fig.canvas.draw()
        # except Exception as e:
        #     print(e)
        #print(frameref_ms-int(time.time()*1000))
        k = cv2.waitKey(int(1000/fps - process_time*1000)) & 0xFF
        if k == 27 or k==ord('q'):
            if playvid == True:
                print("Please stop video before quit")
            else:
                break
        elif k == ord('l'):
            if playvid == False:
                print("Recording Left hand")
                playvid = True
                ret = True
                light_show = False
                counter = 0
                data = []
                open_frame = open_left
                close_frame = close_left
                prepare_frame = prepare_left
                hand = 'left'
                #vid = cv2.VideoCapture('./outvid.mp4')
            else :
                print("Video is running")
        elif k == ord('r'):
            if playvid == False:
                print("Recording Right hand")
                playvid = True
                ret = True
                light_show = False
                counter = 0
                data = []
                open_frame = open_right
                close_frame = close_right
                prepare_frame = prepare_right
                hand = 'right'
                #vid = cv2.VideoCapture('./outvid.mp4')
            else :
                print("Video is running")
        elif k == ord('b'):
            if playvid == False:
                print("Recording Both hand")
                playvid = True
                ret = True
                light_show = False
                counter = 0
                data = []
                open_frame = open_both
                close_frame = close_both
                prepare_frame = prepare_both
                hand = 'both'
                #vid = cv2.VideoCapture('./outvid.mp4')
            else :
                print("Video is running")
        
        elif k == ord('f'):
            if playvid == False:
                print("Recording foot")
                playvid = True
                ret = True
                light_show = False
                counter = 0
                data = []
                open_frame = down_foot
                close_frame = up_foot
                prepare_frame = prepare_foot
                hand = 'foot'
                #vid = cv2.VideoCapture('./outvid.mp4')
            else :
                print("Video is running")

        
        elif k == ord('s'):
            playvid=False

def save_data(sample):
    global data
    global hand
    global light_show
    data.append([i*SCALE_FACTOR for i in sample.channels_data] + [hand, light_show, time.time()])

def start_board():
    board = OpenBCICyton(port=args.port, daisy=True)
    board.start_stream(save_data)

def data_save(save_name):
    global data
    #print(data)
    with open(save_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    

parser = argparse.ArgumentParser()
parser.add_argument('-u','--user',required=True,type=str)
parser.add_argument('-p','--port',default='/dev/tty.usbserial-DM02590B',type=str)
parser.add_argument('-n','--nloop',default=3,type=int)

args = parser.parse_args()


if __name__ == '__main__':
    if not os.path.isdir('bci_data'):
        os.makedirs('bci_data')
    if not os.path.isdir(f'bci_data/{args.user}'):
        os.makedirs(f'bci_data/{args.user}')
    x = threading.Thread(target=start_board)
    x.daemon = True
    x.start()
    main()