"""detection.py"""
import math
from functions import *

dots_enum_hist = []
fall_check = []
hand_check = []


def getSlopes(x1, y1, x2, y2):
    yDiff = abs(y1 - y2)
    xDiff = abs(x1 - x2)
    return yDiff / xDiff


class DotsDetection:
    def __init__(self, list):
        self.list = list
        self.falling = None
        self.raising_hand = None
        self.dots_insert()

    def dots_insert(self):
        global dots_enum_hist
        dots_enum_hist.append(self.list)
        if len(dots_enum_hist) > 5:
            dots_enum_hist.pop(0)
        t1 = th.Thread(target=self.pose)
        t2 = th.Thread(target=self.raise_hand)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def pose(self):
        global fall_check
        left_shoulder = self.list[11][1]
        right_shoulder = self.list[12][1]
        left_hip = self.list[23][1]
        right_hip = self.list[24][1]
        """do pose detection
        First condition: Check shoulders and hip slope is larger than 1
        Second condition: Check shoulders is above hip
        Third condition: Check the depth value is or not larger than threshold
        """
        slope_condition = False
        threshold_xy = round(math.tan(math.radians(45)), 5)
        threshold_zy = round(math.tan(math.radians(45)), 5)
        shoulder_hip_slope_xy = getSlopes((left_shoulder.x + right_shoulder.x) / 2,
                                          (left_shoulder.y + right_shoulder.y) / 2,
                                          (left_hip.x + right_hip.x) / 2, (left_hip.y + right_hip.y) / 2)
        if shoulder_hip_slope_xy > threshold_xy and \
                ((left_shoulder.y + right_shoulder.y) / 2 < (left_hip.y + right_hip.y) / 2):
            """Person is upright to the camera"""
            shoulder_hip_slope_zy = getSlopes((left_shoulder.z + right_shoulder.z) / 2,
                                              (left_shoulder.y + right_shoulder.y) / 2,
                                              (left_hip.z + right_hip.z) / 2, (left_hip.y + right_hip.y) / 2)
            """if the body angle is smaller than 45 degree, aka slope smaller than 1, possible case to fall"""
            slope_condition = shoulder_hip_slope_zy < threshold_zy
        else:
            """Person is inverted or horizontal to the camera"""
            slope_condition = True
        fall_check.append(slope_condition)
        fall = False
        if len(fall_check) > 10:
            fall_check.pop(0)
        if fall_check[-4:] == [True, True, True, True]:
            first = fall_check.index(True)
            fall = first >= 3
        self.falling = fall

    def raise_hand(self):
        right_elbow = self.list[14][1]
        right_wrist = self.list[16][1]
        left_elbow = self.list[13][1]
        left_wrist = self.list[15][1]
        slope = 0
        threshold = round(math.tan(math.radians(60)), 5)
        if right_wrist.y < right_elbow.y:
            slope = getSlopes(right_elbow.x, right_elbow.y, right_wrist.x, right_wrist.y)
        elif left_wrist.y < left_elbow.y:
            slope = getSlopes(left_elbow.x, left_elbow.y, left_wrist.x, left_wrist.y)
        hand_condition = slope > threshold
        hand_check.append(hand_condition)
        hand = False
        if len(hand_check) > 6:
            hand_check.pop(0)
        if False not in hand_check:
            hand = True
        self.raising_hand = hand
