"""main.py"""
from functions import *
from detection import *


"""input dataset from coco"""
config_file = 'config.pbtxt'
frozen_model = 'models.pb'
model = cv2.dnn_DetectionModel(frozen_model, config_file)
model.setInputSize(320, 320)
model.setInputScale(1.0 / 127.5)
model.setInputMean((127.5, 127.5, 127.5))
model.setInputSwapRB(True)

"""detect pose"""
mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

"""reset txt"""
reset_txt()

"""function loop() for booting"""
def loop():
    """have camera ready"""
    video_camera = cv2.VideoCapture(0)
    video_camera.open("https://192.168.68.107:8080/video")

    """generate video output"""
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    x = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    video_file_name = x + ".avi"
    tempp = rescale_frame(video_camera.read()[1], 0.1)
    video_output = cv2.VideoWriter(video_file_name, fourcc, 2.0, (tempp.shape[1], tempp.shape[0]), isColor=False)

    """variables for looping"""
    pTime = 0
    running = True
    # threads = []
    ClassIndex, confidence, bbox = [], [], []

    """Main loop"""
    while running:
        """
            This part gets every frame.
            "img" will be for display.
            "frame" is for detection.
            The output video will be in "frame" format.
        """
        _, img = video_camera.read()
        frame = rescale_frame(img, 0.2)
        now = datetime.now()
        video_output.write(rescale_frame(img, 0.1))

        """
            This part only runs every 0.5 seconds.
            It finds dots and output the dots out using threading.
        """
        p = round(float(now.strftime("%S.%f")), 1)
        if p % 1 == 0.5 or p % 1 == 0:
            """try except to prevent program ending errors"""
            try:
                """dots detection"""
                imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(imgRGB)

                """output unusual activities"""
                if results.pose_landmarks:
                    person = DotsDetection(list(enumerate(results.pose_landmarks.landmark)))
                    if person.falling:
                        screencap = screen_capture(img, now)
                        message_bot("Fall", screencap)
                    if person.raising_hand:
                        screencap = screen_capture(img, now)
                        message_bot("Need Help", screencap)
                """class detection"""
                ClassIndex, confidence, bbox = model.detect(frame, confThreshold=0.65)
            except cv2.error:
                pass

        """
            This part runs for every frame.
            It creates rectangles for every frame,
            althought the detection part of it only runs every 0.5 second.
        """
        object_count = [0, 0, 0]
        if len(ClassIndex) != 0:
            for ClassIND, conf, boxes in zip(ClassIndex.flatten(), confidence.flatten(), bbox):
                if ClassIND == 1:
                    cv2.rectangle(img, boxes*5, rectangle_color, rectangle_thickness)
                    cv2.putText(img, "Person", (boxes[0]*5 + 10, boxes[1]*5 + 40), text_font,
                                fontScale=text_font_scale, color=text_color,
                                thickness=text_thickness)
                    object_count[0] = object_count[0] + 1
                if ClassIND == 62:
                    cv2.rectangle(img, boxes*5, rectangle_color, rectangle_thickness)
                    cv2.putText(img, "chair", (boxes[0]*5 + 10, boxes[1]*5 + 40), text_font,
                                fontScale=text_font_scale, color=text_color,
                                thickness=text_thickness)
                    object_count[1] = object_count[1] + 1
                if ClassIND == 65:
                    cv2.rectangle(img, boxes*5, rectangle_color, rectangle_thickness)
                    cv2.putText(img, "bed", (boxes[0]*5 + 10, boxes[1]*5 + 40), text_font,
                                fontScale=text_font_scale, color=text_color,
                                thickness=text_thickness)
                    object_count[2] = object_count[2] + 1

        """object count"""
        cv2.putText(img, "Person count:" + str(object_count[0]), (10, 30), text_font,
                    fontScale=text_font_scale, color=text_color,
                    thickness=text_thickness)
        cv2.putText(img, "Chair count:" + str(object_count[1]), (10, 60), text_font,
                    fontScale=text_font_scale, color=text_color,
                    thickness=text_thickness)
        cv2.putText(img, "Bed count:" + str(object_count[2]), (10, 90), text_font,
                    fontScale=text_font_scale, color=text_color,
                    thickness=text_thickness)

        """reset object count"""
        object_count = [0, 0, 0]

        """display framerate"""
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img, "fps:" + str("{:.1f}".format(fps)), (10, 120), text_font,
                    fontScale=text_font_scale, color=text_color,
                    thickness=text_thickness)

        """display"""
        single_frame_1 = rescale_frame(img, 0.4)
        cv2.imshow("Video", single_frame_1)

        """break window with space bar"""
        if (cv2.waitKey(1) & 0xFF == ord(' ')) or (int(now.strftime("%H")) == 6):
            """turn off camera and video output, also destory windows"""
            video_camera.release()
            video_output.release()
            cv2.destroyAllWindows()
            running = False

            """save the video"""
            # if input("Save the video?") == "y":
            if True:
                src = path + "/" + video_file_name
                dst = path + "/videos"
                print("Saved.")
                shutil.move(src, dst)
            else:
                os.remove(video_file_name)

st.legacy_caching.clear_cache()

"""booting"""
while True:
    current_time = int(datetime.now().strftime("%H"))
    # if True:
    if current_time > 23 or current_time < 6:
        loop()
    else:
        break
