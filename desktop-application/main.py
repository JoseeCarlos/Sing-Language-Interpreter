import threading
import tkinter as tk
import tkinter.ttk as ttk
import speech_recognition as sr
import pyttsx3
import mediapipe as mp

import cv2
import imutils
import pyvirtualcam
from PIL import Image, ImageTk

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import TensorBoard
import numpy as np
from sklearn.metrics import multilabel_confusion_matrix, accuracy_score
import cv2
import mediapipe as mp
import  time


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
        def camSelection_changed(event):
            None
        #model init
        actions = np.array(['hello', 'thanks', 'i love you'])

        model = Sequential()
        model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(30, 1662)))
        model.add(LSTM(128, return_sequences=True, activation='relu'))
        model.add(LSTM(64, return_sequences=False, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(actions.shape[0], activation='softmax'))
        model.load_weights('action.h5')
        #model functions
        def extract_keypoints(results):
            pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                             results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
            face = np.array([[res.x, res.y, res.z] for res in
                             results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(
                468 * 3)
            lh = np.array([[res.x, res.y, res.z] for res in
                           results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(
                21 * 3)
            rh = np.array([[res.x, res.y, res.z] for res in
                           results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(
                21 * 3)
            return np.concatenate([pose, face, lh, rh])

        colors = [(245, 117, 16), (117, 245, 16), (16, 117, 245)]

        def prob_viz(res, actions, input_frame, colors):
            output_frame = input_frame.copy()
            for num, prob in enumerate(res):
                cv2.rectangle(output_frame, (0, 60 + num * 40), (int(prob * 100), 90 + num * 40), colors[num], -1)
                cv2.putText(output_frame, actions[num], (0, 85 + num * 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 255, 255), 2, cv2.LINE_AA)

            return output_frame
        #funciones mediapipe
        mp_drawing = mp.solutions.drawing_utils

        def mediapipe_detection(image, model):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # COLOR CONVERSION BGR 2 RGB
            image.flags.writeable = False  # Image is no longer writeable
            results = model.process(image)  # Make prediction
            image.flags.writeable = True  # Image is now writeable
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # COLOR COVERSION RGB 2 BGR
            return image, results

        def draw_styled_landmarks(image, results):
            global mp_holistic
            # Draw face connections
            mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
                                      mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                                      mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                                      )
            # Draw pose connections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
                                      )
            # Draw left hand connections
            mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
                                      )
            # Draw right hand connections
            mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                                      mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                      )
        #VideoStream
        video =None
        holistic=None
        mp_holistic=None
        sequence = None
        def videoStream():
            global video
            global mp_holistic
            global holistic
            global sequence
            global sentence
            global threshold
            video=cv2.VideoCapture(self.cameraCombo.current())
            mp_holistic = mp.solutions.holistic
            holistic=mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
            sequence=[]
            sentence = []
            threshold = 0.8
            iniciar()
        def iniciar():
            global video
            global holistic
            global sequence
            global sentence
            global threshold
            ret,frame=video.read()

            cam = pyvirtualcam.Camera(width=1280, height=960, fps=30,device="Unity Video Capture")

            if ret==True:
                frame=imutils.resize(frame,width=1280,height=960)
                frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

                cam.send(frame)
                cam.sleep_until_next_frame()

                #procesado de imagen de entrada
                frame=imutils.resize(frame,width=520,height=330)

                frame, results = mediapipe_detection(frame, holistic)
                draw_styled_landmarks(frame, results)
                keypoints = extract_keypoints(results)

                sequence.append(keypoints)
                sequence = sequence[-30:]

                if len(sequence) == 30:
                    res = model.predict(np.expand_dims(sequence, axis=0))[0]
                    print(actions[np.argmax(res)])
                    # 3. Viz logic
                    if res[np.argmax(res)] > threshold:
                        if len(sentence) > 0:
                            if actions[np.argmax(res)] != sentence[-1]:
                                sentence.append(actions[np.argmax(res)])
                        else:
                            sentence.append(actions[np.argmax(res)])

                    if len(sentence) > 5:
                        sentence = sentence[-5:]

                    # Viz probabilities
                    frame = prob_viz(res, actions, frame, colors)
                cv2.rectangle(frame, (0, 0), (640, 40), (245, 117, 16), -1)
                cv2.putText(frame, ' '.join(sentence), (3, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                #Visualizacion de imagen de entrada
                img=Image.fromarray(frame)
                image=ImageTk.PhotoImage(image=img)

                self.cameraInputImgLabel.configure(image=image)
                self.cameraInputImgLabel.image=image
                self.cameraInputImgLabel.after(10,iniciar)

        def videoStop():
            global video
            self.cameraInputImgLabel.configure(bg="black",image=None)
            self.cameraInputImgLabel.image=None
            video.release()
        #speech reognition
        r = sr.Recognizer()

        def SpeakText(command):
            converter = pyttsx3.init()
            converter.setProperty('rate', 150)
            converter.setProperty('volume', 0.7)
            voices = converter.getProperty('voices')
            converter.setProperty('voice', voices[1].id)
            converter.say(command)
            converter.runAndWait()

        source2=sr.Microphone(1)

        def speechRecognition():
            global t
            t=threading.Thread(target=realTimeSpeech)
            t.start()
        def realTimeSpeech():
            global isActive
            while (isActive==True):
                try:
                    with sr.Microphone(1) as source2:
                        audio2 = r.listen(source2)
                        MyText = r.recognize_google(audio2, language='es-ES')
                        MyText = MyText.lower()
                        SpeakText(MyText)
                        self.realTimeTextLabel.config(text="Texto en tiempo real:\n"+MyText)
                except sr.RequestError as e:
                    print("Could not request results; {0}".format(e))
                except sr.UnknownValueError:
                    print("unknown error occured")
        #stratButton clickEvent
        global buttonStartFlag
        buttonStartFlag =False
        global isActive
        isActive=False
        global t
        t = None
        def startButtonClicked(event):
            global buttonStartFlag
            global isActive
            global t
            if buttonStartFlag==False:
                isActive=True
                videoStream()
                ##speechRecognition()
                self.startButton.config(text="Detener")
                buttonStartFlag=True
            else:
                isActive=False
                videoStop()
                self.startButton.config(text="Iniciar")
                buttonStartFlag=False
                t.join()
        #idiomaComboSeleccion
        idiomas=['es-ES']
        #Componentes de frameCameraConfig
        self.cameraInputImgLabel=tk.Label(self.main,bg="black")
        self.cameraInputImgLabel.place(x=190,y=10,width=520,height=330)

        self.cameraLabel=ttk.Label(self.main,text="Selecciona Webcam")
        self.cameraLabel.place(x=400,y=340)
        self.cameraCombo=ttk.Combobox(self.main,state="readonly",values=returnCameraIndexes())
        self.cameraCombo.current(0)
        self.cameraCombo.bind("<<ComboboxSelected>>", camSelection_changed)
        self.cameraCombo.place(x=190,y=360,width=520)
        self.languageLabel=ttk.Label(self.main,text="Selecciona Idioma")
        self.languageLabel.place(x=400,y=385)
        self.languageCombo=ttk.Combobox(self.main,state="readonly",values=["Español","English"])
        self.languageCombo.current(0)
        self.languageCombo.place(x=190,y=405,width=520)
        self.startButton=ttk.Button(self.main,text="Iniciar")
        self.startButton.bind("<Button-1>",startButtonClicked)
        self.startButton.place(x=375,y=435,width=150)
        #Componentes de frameInterpretationView
        self.realTimeTextLabel=ttk.Label(self.main,text="Texto en tiempo real:")
        self.realTimeTextLabel.place(x=715,y=50,width=180)
        self.realTimeInterpretationTitleLabel=ttk.Label(self.main,text="Interpretacion en Tiempo Real:")
        self.realTimeInterpretationTitleLabel.place(x=715,y=150,width=180)
        self.realTimeInterpretationImg=tk.PhotoImage()
        self.realTimeInterpretationImgLabel=tk.Label(self.main,image=self.realTimeInterpretationImg)
        self.realTimeInterpretationImgLabel.place(x=715,y=170,width=180)
        #Versions
        self.versionLabel=ttk.Label(self.main,text="v1.0")
        self.versionLabel.pack(side="bottom")
        self.main.mainloop()
app=Aplication()