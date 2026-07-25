document.addEventListener('DOMContentLoaded', () => {
    // 🔥 URL sahi karo
    const socket = io('http://127.0.0.1:5000', {
        transports: ['polling', 'websocket'],
        reconnection: true,
        reconnectionAttempts: 10
    });

    let username = 'User' + Math.floor(Math.random() * 1000);
    document.getElementById('usernameDisplay').textContent = username;
    document.getElementById('userAvatar').textContent = username.charAt(0).toUpperCase();

    const messagesContainer = document.getElementById('messagesContainer');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const inputWrapper = document.querySelector('.input-wrapper');

    function scrollToBottom() {
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }

    function appendMessage(sender, text, time, isOwn) {
        const msg = document.createElement('div');
        msg.className = `message ${isOwn ? 'own-message' : 'other-message'}`;

        if (isOwn) {
            msg.innerHTML = `
                <div class="msg-content">
                    <div class="msg-bubble">
                        <p>${text}</p>
                        <span style="font-size:10px; color:#888; text-align:right; display:block;">${time}</span>
                    </div>
                </div>
            `;
        } else {
            msg.innerHTML = `
                <div class="msg-avatar" style="background:#2563eb; color:#fff; border-radius:50%; width:28px; height:28px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold;">${sender.charAt(0).toUpperCase()}</div>
                <div class="msg-content">
                    <div class="msg-header">
                        <span class="msg-name">${sender}</span>
                    </div>
                    <div class="msg-bubble">
                        <p>${text}</p>
                        <span style="font-size:10px; color:#888; display:block;">${time}</span>
                    </div>
                </div>
            `;
        }

        messagesContainer.appendChild(msg);
        scrollToBottom();
    }

    // 🔥 DEBUG LOGS
    socket.on('connect', () => {
        console.log('✅ Connected to server');
        console.log('🔗 Socket ID:', socket.id);
        socket.emit('user-join', username);
    });

    socket.on('connect_error', (err) => {
        console.error('❌ Connection error:', err.message);
    });

    socket.on('receive-message', (data) => {
        console.log('📩 Received:', data);  // 🔥 DEBUG
        if (data.username === username) return;
        appendMessage(data.username, data.text, data.time, false);
    });

    socket.on('user-joined', (name) => {
        if (name !== username) {
            const sys = document.createElement('div');
            sys.className = 'message system-message';
            sys.innerHTML = `<p>${name} joined the chat</p>`;
            messagesContainer.appendChild(sys);
            scrollToBottom();
        }
    });

    socket.on('user-left', (name) => {
        if (name !== username) {
            const sys = document.createElement('div');
            sys.className = 'message system-message';
            sys.innerHTML = `<p>${name} left the chat</p>`;
            messagesContainer.appendChild(sys);
            scrollToBottom();
        }
    });

    // 🔥 SEND WITH ACK
    function sendMessage() {
        const text = messageInput.value.trim();
        if (!text) {
            inputWrapper.classList.add('error');
            setTimeout(() => inputWrapper.classList.remove('error'), 500);
            return;
        }

        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Show locally
        appendMessage(username, text, time, true);

        // Send with ACK
        socket.emit('send-message', {
            username: username,
            text: text,
            time: time
        }, (ack) => {
            console.log('✅ Server ACK:', ack);  // 🔥 DEBUG
        });

        messageInput.value = '';
        messageInput.focus();
    }

    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); sendMessage(); }
    });

    // Sidebar
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const openBtn = document.getElementById('openSidebarBtn');
    const closeBtn = document.getElementById('closeSidebarBtn');

    function toggleSidebar(open) {
        if (open) {
            sidebar.classList.add('open');
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        } else {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    openBtn.addEventListener('click', (e) => { e.stopPropagation(); toggleSidebar(true); });
    closeBtn.addEventListener('click', () => toggleSidebar(false));
    overlay.addEventListener('click', () => toggleSidebar(false));
});