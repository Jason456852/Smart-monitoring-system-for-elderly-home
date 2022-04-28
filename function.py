"""functions.py"""
import cv2
import numpy as np
import os
import shutil
import time
import mediapipe as mp
from datetime import datetime
import threading as th
import streamlit as st
import requests
from dhooks import Webhook, File
import math


"""rectangle setting"""
rectangle_color = (255, 0, 0)
rectangle_thickness = 2

"""text settings"""
text_font_scale = 1
text_font = cv2.FONT_HERSHEY_SIMPLEX
text_color = (0, 255, 0)
text_thickness = 2

"""file path"""
path = str(os.path.dirname(os.path.realpath(__file__)))

"""webhook path"""
webhook = Webhook("URL for discord server")


"""lower resolution"""
def rescale_frame(frame, scale):
    try:
        width = int(frame.shape[1] * scale)
        height = int(frame.shape[0] * scale)
        dim = (width, height)
        return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    except AttributeError:
        return frame

"""screenshot part"""
def screen_capture(frame, time_full):
    png_name = time_full.strftime("%Y-%m-%d-%H-%M-%S") + '.png'
    cv2.imwrite(png_name, frame)
    src = path + "/" + png_name
    dst = path + "/screenshots"
    shutil.move(src, dst)
    return png_name

"""send messages"""
def message_bot(event, filename):
    file_path = File(path + "\\screenshots\\" + filename)
    webhook.send(event, file=file_path)

"""print labels"""
def get_labels():
    labels = []
    filename = 'Labels.txt'
    with open(filename, 'rt') as temp:
        labels = temp.read().rstrip('\n').split('\n')
    print(list(enumerate(labels)))

"""reset txt"""
def reset_txt():
    txt_files = ["lm_0_x.txt", "lm_0_y.txt", "lm_0_z.txt", "lm_11_x.txt", "lm_11_y.txt", "lm_11_z.txt", "lm_12_x.txt", "lm_12_y.txt", "lm_12_z.txt", "lm_23_x.txt", "lm_23_y.txt", "lm_23_z.txt", "lm_24_x.txt", "lm_24_y.txt", "lm_24_z.txt"]
    for i in txt_files:
        f = open(i, "w")
        f.close()

"""delete outdated files"""
def delete_outdated():
    filenames = next(os.walk(path + "\\screenshots"), (None, None, []))[2]
    if len(filenames) >= 10:
        filenames = sorted(filenames)
        os.remove(path + "/screenshots/" + filenames[0])
    filenames = next(os.walk(path + "\\videos"), (None, None, []))[2]
    if len(filenames) >= 10:
        filenames = sorted(filenames)
        os.remove(path + "/videos/" + filenames[0])
