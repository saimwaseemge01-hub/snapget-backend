import socketio
import eventlet
import os
from eventlet import wsgi

sio = socketio.Server(
    cors_allowed_origins='*',
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25
)

users = {}

@sio.event
def connect(sid, environ):
    print(f"✅ Connected: {sid}")
    users[sid] = {'username': 'Guest', 'is_real': False}
    
    sio.emit('receive-message', {
        'username': 'System',
        'text': 'Welcome! Type /name YourName to set username.',
        'time': 'Now',
        'isOwn': False
    }, room=sid)

@sio.event
def disconnect(sid):
    if sid in users:
        user = users[sid]
        if user['is_real'] and user['username'] != 'Guest':
            sio.emit('user-left', user['username'])
            print(f"👋 {user['username']} left")
        del users[sid]
        print(f"❌ Disconnected: {sid}")

@sio.event
def user_join(sid, username):
    if sid in users:
        users[sid]['username'] = username
        users[sid]['is_real'] = True
        sio.emit('user-joined', username)
        print(f"👤 {username} joined")

@sio.event
def send_message(sid, data):
    username = data['username']
    text = data['text']
    time = data.get('time', 'Now')
    
    print(f"💬 SERVER RECEIVED: {username}: {text}")  # 🔥 DEBUG LINE
    
    # Broadcast to ALL clients
    sio.emit('receive-message', {
        'username': username,
        'text': text,
        'time': time,
        'isOwn': False
    })
    
    return {'status': 'ok'}  # 🔥 ACK bhejo

class StaticFileApp:
    def __init__(self):
        self.static_dir = os.path.dirname(os.path.abspath(__file__))
    
    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        
        if path.startswith('/socket.io/'):
            return sio.handle_request(environ, start_response)
        
        if path == '/':
            path = '/chat.html'
        
        file_path = self.static_dir + path
        print(f"📂 Trying to serve: {file_path}")
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
            
            if path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.js'):
                content_type = 'application/javascript'
            elif path.endswith('.html'):
                content_type = 'text/html'
            else:
                content_type = 'text/plain'
            
            start_response('200 OK', [('Content-Type', content_type)])
            return [content]
        
        print(f"❌ File not found: {file_path}")
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'File not found']

app = StaticFileApp()

if __name__ == '__main__':
    print("="*50)
    print("🚀 SERVER STARTING...")
    print("📍 http://127.0.0.1:5000/chat.html")
    print("="*50)
    wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)