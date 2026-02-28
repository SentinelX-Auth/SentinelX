from web_app import app, socketio

if __name__ == '__main__':
    print('Starting Flask (SocketIO) server on 127.0.0.1:5000')
    socketio.run(app, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)
