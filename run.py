import argparse
import tellopy
import numpy as np
import cv2
from time import sleep


current_height = 0
stand = ""
drone_height = 0
drone_speed = 0
can_move = True

def handler(event, sender, data, **args):
    global drone_height, drone_speed
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        print(data)

        drone_height = data.height
        drone_speed = data.ground_speed

def handleFileReceived(event, sender, data):
    global current_height, stand, can_move
    # Create a file in ~/Pictures/ to receive image data from the drone.
    with open(f'{stand}_{current_height}cm.png', 'wb') as fd:
        fd.write(data)
    print('Saved photo')
    can_move = True


def make_photo(height):
    global  current_height, drone_speed, can_move
    while drone_speed != 0:
        sleep(1)
    current_height = height
    can_move = False
    drone.take_picture()
    seconds_passed = 0
    while not can_move:
        sleep(1)
        seconds_passed += 1
        if seconds_passed > 10:
            make_photo(height)


def down(drone, val):
    left_y = val / 100.0 * -1
    if abs(drone.left_y - left_y) > 1e-4:
        drone.down(val)

def up(drone, val):
    left_y = val / 100.0
    if abs(drone.left_y - left_y) > 1e-4:
        drone.up(val)

def height(drone, value):
    global drone_height, can_move
    print(f"==> Moving to height {value}")
    while can_move == False:
        sleep(1)
    value = int(value/10)
    if value == drone_height:
        return
    if value < drone_height:
        while abs(drone_height - value) > 1e-4:
            down_value = 25
            dist = np.abs(drone_height-value)
            if dist > 3:
                down_value = 50
            if dist > 4:
                down_value = 75
            if dist > 5:
                down_value = 100
            down(drone,down_value)
            sleep(0.05)
            if value > drone_height:
                break
        drone.down(0)

    elif value > drone_height:
        while abs(drone_height - value) > 1e-4:
            up_value = 25
            
            dist = np.abs(drone_height-value)
            if dist > 3:
                up_value = 50
            if dist > 4:
                up_value = 75
            if dist > 5:
                up_value = 100
            up(drone, up_value)
            sleep(0.05)
            if value < drone_height:
                break
        drone.up(0)


def back(drone, value):
    global can_move
    while can_move == False:
        sleep(1)
    drone.backward(25)
    sleep(value/100*3.5)
    drone.backward(0)

def forward(drone, value):
    global can_move
    while can_move == False:
        sleep(1)
    drone.forward(25)
    sleep(value/100*3.5)
    drone.forward(0)

parser = argparse.ArgumentParser()
parser.add_argument("stand", help="Stand name")
parser.add_argument("-hs",
                    "--heights",
                    nargs="+",
                    help="Heights to take photos",
                    required=True)
'''
parser.add_argument("-bs",
                    "--back_shifts",
                    nargs="+",
                    help="Back shifts",
                    required=True)
'''

args = parser.parse_args()
stand = args.stand

heights = np.array(args.heights).astype(np.int32)
#back_shifts = np.array(args.back_shifts).astype(np.int32)
min_height = 30

drone = tellopy.Tello()

try:
    drone.subscribe(drone.EVENT_FLIGHT_DATA, handler)
    drone.subscribe(drone.EVENT_FILE_RECEIVED, handleFileReceived)
    drone.connect()
    drone.wait_for_connection(60.0)
    drone.takeoff()
    sleep(5)
    

    for num, shift in enumerate(heights):
        h = heights[num]
        height(drone, h)
        make_photo(h)
        
    drone.land()

except Exception as ex:
    print(ex)
finally:
    drone.land()
    drone.quit()

print("stop")


'''
for num, shift in enumerate(shifts):
    height = heights[num]
    if shift > 0:
        tello.move_up(int(shift))
    if shift < 0:
        tello.move_down(int(-shift))
    for bs in back_shifts:
        if bs != 0:
            tello.move_back(int(bs))
        make_photo(stand, height, bs)
    fw_shift = int(np.sum(back_shifts))
    if fw_shift != 0:
        tello.move_forward(fw_shift)

tello.land()
'''