#!/usr/bin/env python
#from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect#, join_room, leave_room, close_room, rooms

import scipy.io.wavfile
import numpy as np
from collections import OrderedDict
import sys

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, binary=True)
#socketio = SocketIO(app, async_mode=async_mode)
#thread = None
#thread_lock = Lock()


#def background_thread():
#    """Example of how to send server generated events to clients."""
#    count = 0
#    while True:
#        socketio.sleep(10)
#        count += 1
#        socketio.emit('my_response',
#                      {'data': 'Server generated event', 'count': count},
#                      namespace='/test')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


#@socketio.on('my_broadcast_event', namespace='/test')
#def test_broadcast_message(message):
#    session['receive_count'] = session.get('receive_count', 0) + 1
#    emit('my_response',
#         {'data': message['data'], 'count': session['receive_count']},
#         broadcast=True)


#@socketio.on('join', namespace='/test')
#def join(message):
#    join_room(message['room'])
#    session['receive_count'] = session.get('receive_count', 0) + 1
#    emit('my_response',
#         {'data': 'In rooms: ' + ', '.join(rooms()),
#          'count': session['receive_count']})


#@socketio.on('leave', namespace='/test')
#def leave(message):
#    leave_room(message['room'])
#    session['receive_count'] = session.get('receive_count', 0) + 1
#    emit('my_response',
#         {'data': 'In rooms: ' + ', '.join(rooms()),
#          'count': session['receive_count']})


#@socketio.on('close_room', namespace='/test')
#def close(message):
#    session['receive_count'] = session.get('receive_count', 0) + 1
#    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
#                         'count': session['receive_count']},
#         room=message['room'])
#    close_room(message['room'])


#@socketio.on('my_room_event', namespace='/test')
#def send_room_message(message):
#    session['receive_count'] = session.get('receive_count', 0) + 1
#    emit('my_response',
#         {'data': message['data'], 'count': session['receive_count']},
#         room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


#@socketio.on('my_ping', namespace='/test')
#def ping_pong():
#    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    #global thread
    #with thread_lock:
    #    if thread is None:
    #        thread = socketio.start_background_task(target=background_thread)
    session['audio'] = []
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('sample_rate', namespace='/test')
def handle_my_sample_rate(sampleRate):
    session['sample_rate'] = sampleRate
    # send some message to front
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': "sampleRate : %s" % sampleRate, 'count': session['receive_count'] })

@socketio.on('audio', namespace='/test')
def handle_my_custom_event(audio):
    #session['audio'] += audio
    #session['audio'] += audio.values()
    values = OrderedDict(sorted(audio.items(), key=lambda t:int(t[0]))).values()
    session['audio'] += values

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    #my_audio = np.array(session['audio'], np.float32)
    #scipy.io.wavfile.write('out.wav', 44100, my_audio.view('int16'))
    #print(my_audio.view('int16'))

    # https://stackoverflow.com/a/18644461/466693
    sample_rate = session['sample_rate']
    my_audio = np.array(session['audio'], np.float32)
    sindata = np.sin(my_audio)
    scaled = np.round(32767*sindata)
    newdata = scaled.astype(np.int16)
    scipy.io.wavfile.write('out.wav', sample_rate, newdata)

    session['audio'] = []
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)
