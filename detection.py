"""detection.py"""
import math
from functions import *

dots_enum_hist = []
fall_check = []


def dots_insert(list):
    dots_enum_hist.append(list)
    if len(dots_enum_hist) > 5:
        dots_enum_hist.pop(0)
    return pose(dots_enum_hist[len(dots_enum_hist) - 1])  # get most recent list


def slope_insert(condition):
    fall_check.append(condition)
    fall = False
    if len(fall_check) > 10:
        fall_check.pop(0)
    if fall_check[-4:] == [True, True, True, True]:
        first = fall_check.index(True)
        fall = first >= 3
    return fall


def getSlopes(x1, y1, x2, y2):
    yDiff = abs(y1 - y2)
    xDiff = abs(x1 - x2)
    return yDiff / xDiff


def recordLandmark(num, x, y, z):
    filePathX = "lm_" + str(num) + "_x.txt"
    filePathY = "lm_" + str(num) + "_y.txt"
    filePathZ = "lm_" + str(num) + "_z.txt"
    fx = open(filePathX, "a+")
    fy = open(filePathY, "a+")
    fz = open(filePathZ, "a+")
    enterx = str(x) + '\n'
    entery = str(y) + '\n'
    enterz = str(z) + '\n'
    fx.write(enterx)
    fy.write(entery)
    fz.write(enterz)
    fx.close()
    fy.close()
    fz.close()


def pose(list):
    nose = list[0][1]
    left_shoulder = list[11][1]
    right_shoulder = list[12][1]
    left_hip = list[23][1]
    right_hip = list[24][1]
    """record data just for stats to set condition to set constrain"""
    recordLandmark(0, nose.x, nose.y, nose.z)
    recordLandmark(11, left_shoulder.x, left_shoulder.y, left_shoulder.z)
    recordLandmark(12, right_shoulder.x, right_shoulder.y, right_shoulder.z)
    recordLandmark(23, left_hip.x, left_hip.y, left_hip.z)
    recordLandmark(24, right_hip.x, right_hip.y, right_hip.z)

    """do pose detection
    First condition: Check shoulders and hip slope is larger than 1
    Second condition: Check shoulders is above hip
    Third condition: Check the depth value is or not larger than threshold
    """
    threshold_xy = round(math.tan(math.radians(45)), 5)
    shoulder_hip_slope_xy = getSlopes((left_shoulder.x + right_shoulder.x) / 2,
                                      (left_shoulder.y + right_shoulder.y) / 2,
                                      (left_hip.x + right_hip.x) / 2, (left_hip.y + right_hip.y) / 2)
    if shoulder_hip_slope_xy > threshold_xy and \
            ((left_shoulder.y + right_shoulder.y) / 2 < (left_hip.y + right_hip.y) / 2):
        """Person is upright to the camera"""
        """Get the slopes for comparing"""
        shoulder_hip_slope_zy = getSlopes((left_shoulder.z + right_shoulder.z) / 2,
                                          (left_shoulder.y + right_shoulder.y) / 2,
                                          (left_hip.z + right_hip.z) / 2, (left_hip.y + right_hip.y) / 2)
        """if the body angle is smaller than 45 degree, aka slope smaller than 1, possible case to fall"""
        threshold_zy = round(math.tan(math.radians(45)), 5)
        slope_condition = shoulder_hip_slope_zy < threshold_zy
        if slope_insert(slope_condition):
            return True
        else:
            return False
    else:
        """Person is inverted or horizontal to the camera"""
        if slope_insert(True):
            return True
        else:
            return False
