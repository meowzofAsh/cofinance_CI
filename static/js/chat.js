(function() {
  const messagesEl = document.getElementById('chat-messages');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  if (!messagesEl) return;

  const scrollBottom = () => {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  };
  scrollBottom();

  const roomName = messagesEl.dataset.room;
  const currentUserId = messagesEl.dataset.userId;
  const typingIndicator = document.getElementById('typing-indicator');
  const typingText = typingIndicator ? typingIndicator.querySelector('.typing-text') : null;
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');

  let socket = null;
  let typingTimer = null;
  let isTyping = false;

  // WebSocket
  if (roomName && window.WebSocket) {
    try {
      const proto = location.protocol === 'https:' ? 'wss' : 'ws';
      socket = new WebSocket(`${proto}://${location.host}/ws/chat/${roomName}/`);

      socket.onopen = () => {
        socket.send(JSON.stringify({ type: 'status' }));
      };

      socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        switch (data.type) {
          case 'message':
            const isMe = String(data.sender_id) === String(currentUserId);
            appendMessage(data.message, isMe ? 'out' : 'in', data.time);
            break;
          case 'typing':
            if (String(data.user_id) !== String(currentUserId)) {
              showTyping(data.is_typing, data.username);
            }
            break;
          case 'user_status':
            updateOnlineStatus(data.user_id, data.is_online, data.username);
            break;
          case 'online_status':
            if (data.users) {
              Object.keys(data.users).forEach(uid => {
                updateOnlineStatus(uid, data.users[uid].is_online, data.users[uid].username);
              });
            }
            break;
        }
      };

      socket.onerror = () => console.warn('WebSocket non disponible');
      socket.onclose = () => {
        if (statusDot) { statusDot.className = 'status-dot offline'; }
        if (statusText) statusText.textContent = 'Hors ligne';
      };
    } catch (err) { console.warn(err); }
  }

  function appendMessage(text, dir, time) {
    const div = document.createElement('div');
    div.className = 'message ' + dir;
    div.innerHTML = '<div class="message-content">' + escapeHtml(text) + '</div>' +
      '<div class="message-meta">' +
      '<span class="message-time">' + (time || 'maintenant') + '</span>' +
      (dir === 'out' ? '<span class="message-status">✓</span>' : '') +
      '</div>';
    messagesEl.appendChild(div);
    scrollBottom();
  }

  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
  }

  function showTyping(typing, username) {
    if (!typingIndicator) return;
    if (typing) {
      if (typingText) typingText.textContent = (username || "Quelqu'un") + ' écrit...';
      typingIndicator.style.display = 'flex';
    } else {
      typingIndicator.style.display = 'none';
    }
    scrollBottom();
  }

  function updateOnlineStatus(userId, isOnline) {
    if (String(userId) !== String(currentUserId)) {
      if (statusDot) statusDot.className = 'status-dot ' + (isOnline ? 'online' : 'offline');
      if (statusText) statusText.textContent = isOnline ? 'En ligne' : 'Hors ligne';
    }
  }

  // Détection de frappe
  if (input && socket) {
    input.addEventListener('input', function() {
      if (!isTyping) {
        isTyping = true;
        if (socket.readyState === 1) socket.send(JSON.stringify({ type: 'typing', is_typing: true }));
      }
      clearTimeout(typingTimer);
      typingTimer = setTimeout(function() {
        isTyping = false;
        if (socket && socket.readyState === 1) socket.send(JSON.stringify({ type: 'typing', is_typing: false }));
      }, 1500);
    });
  }

  // Envoi
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      var val = input.value.trim();
      if (!val) return;

      // WebSocket disponible
      if (socket && socket.readyState === 1) {
        socket.send(JSON.stringify({ message: val }));
        input.value = '';
        isTyping = false;
        clearTimeout(typingTimer);
        if (socket.readyState === 1) socket.send(JSON.stringify({ type: 'typing', is_typing: false }));
        return;
      }

      // Fallback HTTP POST (AJAX)
      var csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
      var xhr = new XMLHttpRequest();
      xhr.open('POST', form.action || window.location.href, true);
      xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      xhr.setRequestHeader('X-CSRFToken', csrf);
      xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      xhr.onload = function() {
        if (xhr.status === 200) {
          try {
            var d = JSON.parse(xhr.responseText);
            appendMessage(val, 'out', d.time || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
          } catch(_) {
            appendMessage(val, 'out', new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
          }
        }
      };
      xhr.send('message=' + encodeURIComponent(val) + '&csrfmiddlewaretoken=' + encodeURIComponent(csrf));
      input.value = '';
      isTyping = false;
      clearTimeout(typingTimer);
    });
  }
})();
