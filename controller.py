import tkinter.messagebox
from tkinter import Tk, Canvas, Button, PhotoImage
import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import cv2 as cv
import numpy as np
import screen_brightness_control as scb
from cvzone.HandTrackingModule import HandDetector


def senceVolumeStart(window_name, volume_window):
    cap = cv2.VideoCapture(0)
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volbar = 400
    volper = 0

    volMin, volMax = volume.GetVolumeRange()[:2]

    while True:
        success, img = cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        lmList = []
        if results.multi_hand_landmarks:
            for handlandmark in results.multi_hand_landmarks:
                for id, lm in enumerate(handlandmark.landmark):
                    h, w, _ = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

        if lmList != []:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cv2.circle(img, (x1, y1), 4, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 4, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

            length = hypot(x2 - x1, y2 - y1)
            vol = np.interp(length, [30, 350], [volMin, volMax])
            volbar = np.interp(length, [30, 350], [400, 150])
            volper = np.interp(length, [30, 350], [0, 100])
            volume.SetMasterVolumeLevel(vol, None)

            cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255), 4)
            cv2.rectangle(img, (50, int(volbar)), (85, 400), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, f"{int(volper)}%", (10, 40), cv2.FONT_ITALIC, 1, (0, 255, 98), 3)

        cv2.imshow(window_name, img)
        key = cv2.waitKey(1)
        if key == 27:  # Pressing Esc key to close only this window
            cv2.destroyWindow(window_name)
            volume_window.destroy()
            break

    cap.release()


def senceBrightnessStart(window_name, brightness_window):
    cap = cv.VideoCapture(0)
    hd = HandDetector()
    val = 0

    while 1:
        _, img = cap.read()
        hands, img = hd.findHands(img)

        if hands:
            lm = hands[0]['lmList']

            length, info, img = hd.findDistance(lm[8][0:2], lm[4][0:2], img)
            blevel = np.interp(length, [30, 350], [0, 100])
            val = np.interp(length, [30, 350], [400, 150])

            blevel = int(blevel)

            scb.set_brightness(blevel)

            cv.rectangle(img, (50, 150), (85, 400), (0, 255, 255), 4)
            cv.rectangle(img, (50, int(val)), (85, 400), (0, 0, 255), -1)
            cv.putText(img, str(blevel) + '%', (20, 430), cv.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

        cv2.imshow(window_name, img)
        key = cv2.waitKey(1)
        if key == 27:  # Pressing Esc key to close only this window
            cv2.destroyWindow(window_name)
            brightness_window.destroy()
            break

    # brightness_window.deiconify()
    cap.release()

class HomeScreen:

    def brightnessStart(self):
        brightness_window = Tk()
        brightness_window.eval('tk::PlaceWindow %s center' % brightness_window.winfo_toplevel())
        brightness_window.withdraw()
        tkinter.messagebox.showinfo('Exiting Program Method', 'Press Escape (esc) key to exit the brightness screen.')
        senceBrightnessStart("WaveMaster: Hand-Guided Brightness", brightness_window)

    def volumeStart(self):
        volume_window = Tk()
        volume_window.eval('tk::PlaceWindow %s center' % volume_window.winfo_toplevel())
        volume_window.withdraw()
        tkinter.messagebox.showinfo('Exiting Program Method', 'Press Escape (esc) key to exit the volume screen.')
        senceVolumeStart("WaveMaster: Hand-Guided Sound", volume_window)

    def aboutUsCommand(self):
        self.window.destroy()
        AboutUsScreen()

    def center_window(self):
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.window.winfo_width()) // 2
        y = (screen_height - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")

    def __init__(self):
        self.window = Tk()
        self.window.geometry("862x519")
        self.window.configure(bg="#121212")
        self.window.title('WaveMaster: Hand-Guided Brightness & Sound')
        self.center_window()
        canvas = Canvas(
            self.window,
            bg="#121212",
            height=519,
            width=862,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.place(x=0, y=0)
        button_image_1 = PhotoImage(
            file="assets/button_1_home.png")
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.aboutUsCommand(),
            relief="flat"
        )
        button_1.place(
            x=320.99999999999994,
            y=386.0,
            width=224.0,
            height=74.0
        )

        button_image_2 = PhotoImage(
            file="assets/button_2_home.png")
        button_2 = Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command= lambda: self.brightnessStart(),
            relief="flat"
        )
        button_2.place(
            x=90.99999999999994,
            y=142.0,
            width=183.0,
            height=154.0
        )

        button_image_3 = PhotoImage(
            file="assets/button_3_home.png")
        button_3 = Button(
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.volumeStart(),
            relief="flat"
        )
        button_3.place(
            x=576.0,
            y=142.0,
            width=184.0,
            height=154.0
        )

        image_image_1 = PhotoImage(
            file="assets/image_1_home.png")
        image_1 = canvas.create_image(
            431.0,
            36.0,
            image=image_image_1
        )
        self.window.resizable(False, False)
        self.window.mainloop()

class AboutUsScreen:
    def homeScreen(self):
        self.window.destroy()
        HomeScreen()

    def center_window(self):
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.window.winfo_width()) // 2
        y = (screen_height - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")


    def __init__(self):
        self.window = Tk()
        self.window.geometry("862x519")
        self.window.configure(bg = "#FFFFFF")
        self.window.resizable(False, False)
        self.window.title('WaveMaster: Hand-Guided Brightness & Sound')
        self.center_window()


        canvas = Canvas(
            self.window,
            bg = "#FFFFFF",
            height = 519,
            width = 862,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        canvas.place(x = 0, y = 0)
        image_image_1 = PhotoImage(
            file="assets/image_1_aboutUs.png")
        image_1 = canvas.create_image(
            431.0000000000001,
            259.00000000000006,
            image=image_image_1
        )

        image_image_2 = PhotoImage(
            file="assets/image_2_aboutUs.png")
        image_2 = canvas.create_image(
            653.0000000000001,
            391.99999999999994,
            image=image_image_2
        )

        image_image_3 = PhotoImage(
            file="assets/image_3_aboutUs.png")
        image_3 = canvas.create_image(
            199.0000000000001,
            107.99999999999994,
            image=image_image_3
        )

        image_image_4 = PhotoImage(
            file="assets/image_4_aboutUs.png")
        image_4 = canvas.create_image(
            750.0000000000001,
            178.99999999999994,
            image=image_image_4
        )

        image_image_5 = PhotoImage(
            file="assets/image_5_aboutUs.png")
        image_5 = canvas.create_image(
            535.0000000000001,
            179.99999999999994,
            image=image_image_5
        )

        canvas.create_text(
            156.0000000000001,
            485.99999999999994,
            anchor="nw",
            text="Punit Kumar Mishra\nEN20CS301326",
            fill="#FFFFFF",
            font=("Jua Regular", 13 * -1)
        )

        image_image_6 = PhotoImage(
            file="assets/image_6_aboutUs.png")
        image_6 = canvas.create_image(
            213.0000000000001,
            414.99999999999994,
            image=image_image_6
        )

        canvas.create_text(
            272.0000000000001,
            308.99999999999994,
            anchor="nw",
            text="Radhika Patidar\nEN20CS301328",
            fill="#FFFFFF",
            font=("Jua Regular", 13 * -1)
        )

        image_image_7 = PhotoImage(
            file="assets/image_7_aboutUs.png")
        image_7 = canvas.create_image(
            331.0000000000001,
            243.99999999999994,
            image=image_image_7
        )

        canvas.create_text(
            28.000000000000114,
            306.99999999999994,
            anchor="nw",
            text="Prashant Ranjan SIngh\nEN20CS301308",
            fill="#FFFFFF",
            font=("Jua Regular", 13 * -1)
        )

        image_image_8 = PhotoImage(
            file="assets/image_8_aboutUs.png")
        image_8 = canvas.create_image(
            97.00000000000011,
            243.99999999999994,
            image=image_image_8
        )

        image_image_9 = PhotoImage(
            file="assets/image_9_aboutUs.png")
        image_9 = canvas.create_image(
            431.0,
            30.0,
            image=image_image_9
        )

        image_image_10 = PhotoImage(
            file="assets/image_10_aboutUs.png")
        image_10 = canvas.create_image(
            419.0000000000001,
            283.99999999999994,
            image=image_image_10
        )

        button_image_1 = PhotoImage(
            file="assets/button_1_aboutUs.png")
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.homeScreen(),
            relief="flat"
        )
        button_1.place(
            x=15.000000000000114,
            y=9.999999999999943,
            width=49.0,
            height=32.0
        )
        self.window.mainloop()

if __name__ == "__main__":
    home_screen = HomeScreen()
