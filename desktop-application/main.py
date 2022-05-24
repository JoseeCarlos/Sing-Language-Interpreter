import tkinter as tk
import tkinter.ttk as ttk
import cv2
import imutils
from PIL import Image, ImageTk
import pyvirtualcam
import numpy as np
from tkinter import messagebox
class Aplication:
    def __init__(self):
        self.main = tk.Tk()
        #Copnfiguracion de ventana
        self.main.title("SLI")
        self.main.geometry("900x480")
        self.main.resizable(0,0)
        #Componentes de frameInstructions
        self.useInstructionsLabel=ttk.Label(self.main,text="Instrucciones de uso: \n   1. Selecciona la webcam.\n   2. Selecciona el idioma.\n   3.Iniciar")
        self.useInstructionsLabel.place(x=10,y=120,width=180)
        self.useInstructionsLabel=ttk.Label(self.main,text="Instrucciones en Aplicación:\n   1. Entrar aconfiguraciones de\n       entrada y salida.\n   2.Selecciona como web cam:\n      SLI Virtual Camera.\n   3. Selecciona como microfono:\n      SLI Virtual Mic.\n   4. Selecciona como Altavoz:\n      SLI Virtual Speaker")
        self.useInstructionsLabel.place(x=10,y=170,width=180)
        #CameraList
        def returnCameraIndexes():
            index = 0
            arr = []
            i = 10
            while i > 0:
                cap = cv2.VideoCapture(index,cv2.CAP_DSHOW)
                if cap.read()[0]:
                    arr.append('CAM'+str(index))
                    cap.release()
                index += 1
                i -= 1
            return arr
        #cambio de seleccion combo camara
        def selection_changed(event):
            None

        #VideoStream
        video =None
        def videoStream():
            global video
            video=cv2.VideoCapture(self.cameraCombo.current())
            iniciar()
        def iniciar():
            global video
            ret,frame=video.read()

            cam = pyvirtualcam.Camera(width=520, height=390, fps=30)
            if ret==True:
                frame=imutils.resize(frame,width=520,height=330)
                frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                img=Image.fromarray(frame)
                image=ImageTk.PhotoImage(image=img)

                cam.send(frame)
                cam.sleep_until_next_frame()

                self.cameraInputImgLabel.configure(image=image)
                self.cameraInputImgLabel.image=image
                self.cameraInputImgLabel.after(10,iniciar)

        def videoStop():
            global video
            self.cameraInputImgLabel.configure(bg="black",image=None)
            self.cameraInputImgLabel.image=None
            video.release()
        #stratButton clickEvent
        global buttonStartFlag
        buttonStartFlag =False
        def buttonClicked(event):
            global buttonStartFlag
            if buttonStartFlag==False:
                videoStream()
                self.startButton.config(text="Detener")
                buttonStartFlag=True
            else:
                videoStop()
                self.startButton.config(text="Iniciar")
                buttonStartFlag=False

        #Componentes de frameCameraConfig
        self.cameraInputImgLabel=tk.Label(self.main,bg="black")
        self.cameraInputImgLabel.place(x=190,y=10,width=520,height=330)

        self.cameraLabel=ttk.Label(self.main,text="Selecciona Webcam")
        self.cameraLabel.place(x=400,y=340)
        self.cameraCombo=ttk.Combobox(self.main,state="readonly",values=returnCameraIndexes())
        self.cameraCombo.current(0)
        self.cameraCombo.bind("<<ComboboxSelected>>", selection_changed)
        self.cameraCombo.place(x=190,y=360,width=520)
        self.languageLabel=ttk.Label(self.main,text="Selecciona Idioma")
        self.languageLabel.place(x=400,y=385)
        self.languageCombo=ttk.Combobox(self.main,state="readonly",values=["Español","English"])
        self.languageCombo.current(0)
        self.languageCombo.place(x=190,y=405,width=520)
        self.startButton=ttk.Button(self.main,text="Iniciar")
        self.startButton.bind("<Button-1>",buttonClicked)
        self.startButton.place(x=375,y=435,width=150)
        #Componentes de frameInterpretationView
        self.realTimeTextLabel=ttk.Label(self.main,text="Texto en tiempo real:\n   ......ipsum dolor sit amet \nconsectetur adipiscing elit, sed \n do eiusmod tempor incididunt \nut labore et dolore magna aliqua.\nFames ac turpis egestas sed.....")
        self.realTimeTextLabel.place(x=715,y=50,width=180)
        self.realTimeInterpretationTitleLabel=ttk.Label(self.main,text="Interpretacion en Tiempo Real:")
        self.realTimeInterpretationTitleLabel.place(x=715,y=150,width=180)
        self.realTimeInterpretationImg=tk.PhotoImage(file="Interpreter.gif")
        self.realTimeInterpretationImgLabel=tk.Label(self.main,image=self.realTimeInterpretationImg)
        self.realTimeInterpretationImgLabel.place(x=715,y=170,width=180)
        #Versions
        self.versionLabel=ttk.Label(self.main,text="v1.0")
        self.versionLabel.pack(side="bottom")
        self.main.mainloop()
app=Aplication()