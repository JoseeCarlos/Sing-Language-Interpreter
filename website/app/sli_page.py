from flask import (
    Blueprint, render_template, Response, request, redirect, url_for, flash,
)
import cv2
bp = Blueprint('sli_page', __name__, url_prefix='/')

camera=cv2.VideoCapture(0)

def generate_frames():
    while True:
        success,frame=camera.read()
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()
        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@bp.route('/', methods=['GET'])
def index():
    return render_template('homepage/index.html')

@bp.route('/features', methods=['GET'])
def features():
    return render_template('features/index.html')

@bp.route('/news', methods=['GET'])
def news():
    return render_template('news/index.html')

@bp.route('/test', methods=['GET'])
def test():
    return render_template('test/index.html')
    
@bp.route('/suport', methods=['GET'])
def suport():
    return render_template('suport/index.html')

@bp.route('/video_feed', methods=['GET'])
def video_feed():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')
    


    