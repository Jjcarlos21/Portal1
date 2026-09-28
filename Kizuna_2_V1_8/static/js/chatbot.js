/**
 * Kizuna Chatbot Widget
 * Se comunica exclusivamente con el backend Flask (/api/chat)
 */

(function () {
    const style = document.createElement('style');
    style.innerHTML = `
        :root {
            --cb-primary: #e65100;
            --cb-primary-dark: #bf360c;
            --cb-primary-light: #ff6d00;
            --cb-bg: #ffffff;
            --cb-surface: #f8f5f2;
            --cb-border: #e8e0da;
            --cb-text: #2d2320;
            --cb-text-muted: #7a6a64;
        }
        #kizuna-chatbot-btn {
            position: fixed;
            bottom: 28px;
            right: 28px;
            width: 62px;
            height: 62px;
            background: linear-gradient(135deg, var(--cb-primary), var(--cb-primary-light));
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 9998;
            box-shadow: 0 4px 20px rgba(230,81,0,0.45);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border: none;
        }
        #kizuna-chatbot-btn:hover { transform: scale(1.10); box-shadow: 0 6px 28px rgba(230,81,0,0.60); }
        #kizuna-chatbot-window {
            position: fixed;
            bottom: 104px;
            right: 28px;
            width: 370px;
            height: 530px;
            background: var(--cb-bg);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(230,81,0,0.18), 0 2px 8px rgba(0,0,0,0.10);
            display: none;
            flex-direction: column;
            overflow: hidden;
            z-index: 9999;
            border: 1px solid var(--cb-border);
            font-family: 'Inter', 'Segoe UI', sans-serif;
            animation: cb-slide-in 0.25s ease;
        }
        #kizuna-chatbot-window.open { display: flex; }
        @keyframes cb-slide-in {
            from { opacity: 0; transform: translateY(20px) scale(0.97); }
            to   { opacity: 1; transform: translateY(0) scale(1); }
        }
        #kizuna-chatbot-header {
            background: linear-gradient(135deg, var(--cb-primary), var(--cb-primary-light));
            color: white;
            padding: 14px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }
        .cb-title-wrap { display: flex; align-items: center; gap: 10px; }
        .cb-avatar { width: 36px; height: 36px; background: rgba(255,255,255,0.25); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; }
        .cb-titles { display: flex; flex-direction: column; }
        .cb-name { font-weight: 700; font-size: 0.95rem; }
        .cb-status { font-size: 0.72rem; opacity: 0.85; display: flex; align-items: center; gap: 4px; }
        .cb-dot { width: 7px; height: 7px; background: #69ff47; border-radius: 50%; box-shadow: 0 0 6px #69ff47; }
        #kizuna-chatbot-close {
            background: rgba(255,255,255,0.18);
            border: none; color: white;
            border-radius: 8px;
            width: 30px; height: 30px;
            cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            font-size: 15px;
            transition: background 0.15s;
        }
        #kizuna-chatbot-close:hover { background: rgba(255,255,255,0.32); }

        #kizuna-chatbot-messages {
            flex: 1;
            padding: 16px 14px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
            background: var(--cb-surface);
        }
        #kizuna-chatbot-messages::-webkit-scrollbar { width: 4px; }
        #kizuna-chatbot-messages::-webkit-scrollbar-thumb { background: #d0c8c4; border-radius: 4px; }
        .cb-msg {
            max-width: 86%;
            padding: 10px 14px;
            border-radius: 16px;
            font-size: 0.875rem;
            line-height: 1.5;
            word-wrap: break-word;
        }
        .cb-msg.bot { background: white; color: var(--cb-text); align-self: flex-start; border-bottom-left-radius: 4px; box-shadow: 0 1px 4px rgba(0,0,0,0.07); }
        .cb-msg.user { background: linear-gradient(135deg, var(--cb-primary), var(--cb-primary-light)); color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        .cb-msg.error { background: #fff0f0; color: #c62828; border: 1px solid #ffcdd2; align-self: flex-start; border-bottom-left-radius: 4px; font-size: 0.82rem; }
        .cb-typing { display: flex; gap: 5px; align-items: center; padding: 12px 16px; background: white; border-radius: 16px; border-bottom-left-radius: 4px; align-self: flex-start; box-shadow: 0 1px 4px rgba(0,0,0,0.07); }
        .cb-typing span { width: 7px; height: 7px; background: var(--cb-primary); border-radius: 50%; animation: cb-bounce 1.2s infinite; opacity: 0.6; }
        .cb-typing span:nth-child(2) { animation-delay: 0.2s; }
        .cb-typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes cb-bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-6px)} }

        #kizuna-chatbot-input-container {
            padding: 12px;
            background: white;
            border-top: 1px solid var(--cb-border);
            display: flex;
            gap: 8px;
            align-items: center;
            flex-shrink: 0;
        }
        #kizuna-chatbot-input {
            flex: 1;
            padding: 10px 14px;
            border: 1.5px solid var(--cb-border);
            border-radius: 22px;
            outline: none;
            font-family: inherit;
            font-size: 0.875rem;
            color: var(--cb-text);
            background: var(--cb-surface);
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        #kizuna-chatbot-input:focus { border-color: var(--cb-primary); box-shadow: 0 0 0 3px rgba(230,81,0,0.10); background: white; }
        #kizuna-chatbot-send {
            background: linear-gradient(135deg, var(--cb-primary), var(--cb-primary-light));
            color: white; border: none;
            width: 42px; height: 42px;
            border-radius: 50%;
            cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            transition: transform 0.15s;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(230,81,0,0.30);
        }
        #kizuna-chatbot-send:hover { transform: scale(1.08); }
        #kizuna-chatbot-send:disabled { opacity: 0.5; cursor: default; transform: none; }
    `;
    document.head.appendChild(style);

    const wrap = document.createElement('div');
    wrap.innerHTML = `
        <button id="kizuna-chatbot-btn" title="Hablar con Kizuna AI" aria-label="Abrir chatbot">
            <svg xmlns="http://www.w3.org/2000/svg" height="26px" viewBox="0 0 24 24" width="26px" fill="#FFF"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/></svg>
        </button>
        <div id="kizuna-chatbot-window" role="dialog" aria-label="Chat Kizuna AI">
            <div id="kizuna-chatbot-header">
                <div class="cb-title-wrap">
                    <div class="cb-avatar">🌸</div>
                    <div class="cb-titles">
                        <span class="cb-name">Kizuna AI</span>
                        <span class="cb-status"><span class="cb-dot"></span>En línea</span>
                    </div>
                </div>
                <button id="kizuna-chatbot-close" aria-label="Cerrar">✕</button>
            </div>
            <div id="kizuna-chatbot-messages" aria-live="polite">
                <div class="cb-msg bot">
                    👋 ¡Hola! Soy el asistente de <strong>Kizuna Venezuela</strong>.<br>
                    Puedo ayudarte con información sobre <strong>Becas MEXT</strong>, <strong>Cultura Japonesa</strong> y actividades del portal.<br><br>
                    ¿En qué puedo ayudarte hoy?
                </div>
            </div>
            <div id="kizuna-chatbot-input-container">
                <input type="text" id="kizuna-chatbot-input" placeholder="Escribe tu pregunta..." autocomplete="off" maxlength="500"/>
                <button id="kizuna-chatbot-send" aria-label="Enviar">
                    <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 0 24 24" width="20px" fill="#FFF"><path d="M0 0h24v24H0V0z" fill="none"/><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(wrap);

    const btn      = document.getElementById('kizuna-chatbot-btn');
    const windowEl = document.getElementById('kizuna-chatbot-window');
    const closeBtn = document.getElementById('kizuna-chatbot-close');
    const msgInput = document.getElementById('kizuna-chatbot-input');
    const sendBtn  = document.getElementById('kizuna-chatbot-send');
    const msgBox   = document.getElementById('kizuna-chatbot-messages');

    let history = [];

    if (sessionStorage.getItem('kizuna_chat_history')) {
        try {
            history = JSON.parse(sessionStorage.getItem('kizuna_chat_history'));
            history.forEach(item => {
                const text = item.parts[0].text;
                appendMsg(text, item.role === 'user' ? 'user' : 'bot');
            });
        } catch (e) { history = []; }
    }

    btn.addEventListener('click', () => {
        windowEl.classList.toggle('open');
        if (windowEl.classList.contains('open')) msgInput.focus();
    });
    closeBtn.addEventListener('click', () => windowEl.classList.remove('open'));

    function appendMsg(text, type) {
        const d = document.createElement('div');
        d.className = 'cb-msg ' + type;
        if (type !== 'user') {
            d.innerHTML = text
                .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
                .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
                .replace(/\*(.*?)\*/g,'<em>$1</em>')
                .replace(/^- (.+)$/gm,'• $1')
                .replace(/\n/g,'<br>');
        } else {
            d.textContent = text;
        }
        msgBox.appendChild(d);
        msgBox.scrollTop = msgBox.scrollHeight;
        return d;
    }

    function showTyping() {
        const d = document.createElement('div');
        d.id = 'cb-typing'; d.className = 'cb-typing';
        d.innerHTML = '<span></span><span></span><span></span>';
        msgBox.appendChild(d); msgBox.scrollTop = msgBox.scrollHeight;
    }
    function hideTyping() { const e = document.getElementById('cb-typing'); if(e) e.remove(); }

    async function sendMessage() {
        const text = msgInput.value.trim();
        if (!text || sendBtn.disabled) return;
        
        appendMsg(text, 'user');
        msgInput.value = '';
        sendBtn.disabled = true;
        msgInput.disabled = true;
        showTyping();

        history.push({ role: 'user', parts: [{ text }] });

        try {
            // Se usa la ruta absoluta /api/chat para responder desde cualquier página del sitio
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ contents: history })
            });

            const data = await res.json();
            hideTyping();

            if (!res.ok) {
                const errDetail = typeof data.error === 'string' ? data.error : JSON.stringify(data.error);
                throw new Error(errDetail || 'Error en la solicitud');
            }

            const reply = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'Sin respuesta del modelo.';
            history.push({ role: 'model', parts: [{ text: reply }] });
            sessionStorage.setItem('kizuna_chat_history', JSON.stringify(history));
            appendMsg(reply, 'bot');
        } catch(err) {
            hideTyping();
            history.pop();
            appendMsg('⚠️ ' + err.message, 'error');
        } finally {
            sendBtn.disabled = false;
            msgInput.disabled = false;
            msgInput.focus();
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    msgInput.addEventListener('keypress', e => { if(e.key === 'Enter') sendMessage(); });
})();