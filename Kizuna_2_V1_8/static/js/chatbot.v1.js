/**
 * Kizuna Chatbot Widget
 * Llama directamente a la API de Gemini desde el navegador.
 */

(function () {

    // Instrucción del sistema
    const SYSTEM_INSTRUCTION = `Eres el asistente virtual oficial de **Kizuna Venezuela**, 
el portal de cultura japonesa y Becas MEXT para Venezuela.

Tu misión es ayudar a los usuarios con información sobre:
- **Becas MEXT**: tipos de becas (pregrado, posgrado, investigación, docente, Nikkei, KOSEN, STC), 
  requisitos, proceso de aplicación, documentos necesarios, fechas y convocatorias.
- **Cultura Japonesa**: artes marciales (Aikido, Judo, Karate, Kendo, Sumo), artes tradicionales 
  (Bonsái, Cerámica, Ceremonia del Té, Shodo, Origami, Taiko), entretenimiento (Manga, Cosplay, Anime),
  gastronomía japonesa, idioma japonés y danza Butoh.
- **Kizuna Venezuela**: eventos, noticias, directorios de instructores y academias en Venezuela.

Responde siempre en **español**, de forma clara, amigable y concisa.
Si no tienes información específica, sugiere al usuario visitar la sección correspondiente del sitio web.
Usa formato markdown básico cuando ayude a la claridad (negritas, listas).`;

    // CSS
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
        #cb-header-actions { display: flex; gap: 6px; }
        #kizuna-chatbot-settings-btn, #kizuna-chatbot-close {
            background: rgba(255,255,255,0.18);
            border: none; color: white;
            border-radius: 8px;
            width: 30px; height: 30px;
            cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            font-size: 15px;
            transition: background 0.15s;
        }
        #kizuna-chatbot-settings-btn:hover, #kizuna-chatbot-close:hover { background: rgba(255,255,255,0.32); }

        /* Panel API Key */
        #cb-apikey-panel {
            background: var(--cb-surface);
            border-bottom: 1px solid var(--cb-border);
            padding: 12px 14px;
            display: none;
            flex-direction: column;
            gap: 8px;
            flex-shrink: 0;
        }
        #cb-apikey-panel.open { display: flex; }
        #cb-apikey-panel label { font-size: 0.78rem; font-weight: 600; color: var(--cb-text-muted); }
        .cb-apikey-row { display: flex; gap: 6px; }
        #cb-apikey-input {
            flex: 1;
            padding: 7px 10px;
            border: 1.5px solid var(--cb-border);
            border-radius: 8px;
            font-size: 0.82rem;
            font-family: monospace;
            outline: none;
            background: white;
            color: var(--cb-text);
            transition: border-color 0.2s;
        }
        #cb-apikey-input:focus { border-color: var(--cb-primary); }
        #cb-apikey-save {
            background: var(--cb-primary);
            color: white; border: none;
            border-radius: 8px;
            padding: 7px 12px;
            font-size: 0.82rem; font-weight: 600;
            cursor: pointer;
        }
        #cb-apikey-save:hover { background: var(--cb-primary-dark); }
        #cb-apikey-hint { font-size: 0.72rem; color: var(--cb-text-muted); }
        #cb-apikey-hint a { color: var(--cb-primary); }

        /* Mensajes */
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

        /* Input */
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
        @media(prefers-color-scheme:dark){
            #kizuna-chatbot-window{background:#1e1a18;border-color:#3a3230;}
            #kizuna-chatbot-messages{background:#161210;}
            .cb-msg.bot{background:#2a2422;color:#f0ebe8;}
            #kizuna-chatbot-input-container{background:#1e1a18;border-color:#3a3230;}
            #kizuna-chatbot-input{background:#2a2422;color:#f0ebe8;border-color:#3a3230;}
            #cb-apikey-panel{background:#1e1a18;border-color:#3a3230;}
            #cb-apikey-input{background:#2a2422;color:#f0ebe8;border-color:#3a3230;}
            .cb-typing{background:#2a2422;}
        }
        @media(max-width:420px){
            #kizuna-chatbot-window{width:calc(100vw - 20px);right:10px;bottom:90px;}
        }
    `;
    document.head.appendChild(style);

    // HTML
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
                <div id="cb-header-actions">
                    <button id="kizuna-chatbot-settings-btn" title="Configurar API Key">⚙️</button>
                    <button id="kizuna-chatbot-close" aria-label="Cerrar">✕</button>
                </div>
            </div>
            <div id="cb-apikey-panel">
                <label>🔑 GEMINI API KEY</label>
                <div class="cb-apikey-row">
                    <input type="password" id="cb-apikey-input" placeholder="AIza..." autocomplete="off"/>
                    <button id="cb-apikey-save">Guardar</button>
                </div>
                <span id="cb-apikey-hint">
                    Obtén tu clave gratis en <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener">Google AI Studio</a>. Se guarda solo en tu navegador.
                </span>
            </div>
            <div id="kizuna-chatbot-messages" aria-live="polite">
                <div class="cb-msg bot">
                    👋 ¡Hola! Soy el asistente de <strong>Kizuna Venezuela</strong>.<br>
                    Puedo ayudarte con <strong>Becas MEXT</strong> y <strong>Cultura Japonesa</strong>.<br><br>
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

    // Referencias
    const btn         = document.getElementById('kizuna-chatbot-btn');
    const windowEl    = document.getElementById('kizuna-chatbot-window');
    const closeBtn    = document.getElementById('kizuna-chatbot-close');
    const settingsBtn = document.getElementById('kizuna-chatbot-settings-btn');
    const apikeyPanel = document.getElementById('cb-apikey-panel');
    const apikeyInput = document.getElementById('cb-apikey-input');
    const apikeySave  = document.getElementById('cb-apikey-save');
    const msgInput    = document.getElementById('kizuna-chatbot-input');
    const sendBtn     = document.getElementById('kizuna-chatbot-send');
    const msgBox      = document.getElementById('kizuna-chatbot-messages');

    const STORAGE_KEY = 'kizuna_gemini_key';
    const history     = [];

    function getKey() { return window.KIZUNA_GEMINI_KEY || localStorage.getItem(STORAGE_KEY) || ''; }
    function saveKey(k) { localStorage.setItem(STORAGE_KEY, k.trim()); }

    // Toggle ventana
    btn.addEventListener('click', () => {
        windowEl.classList.toggle('open');
        if (windowEl.classList.contains('open')) {
            if (!getKey()) { apikeyPanel.classList.add('open'); apikeyInput.focus(); }
            else msgInput.focus();
        }
    });
    closeBtn.addEventListener('click', () => {
        windowEl.classList.remove('open');
        apikeyPanel.classList.remove('open');
    });

    // Toggle settings
    settingsBtn.addEventListener('click', () => {
        apikeyPanel.classList.toggle('open');
        if (apikeyPanel.classList.contains('open')) {
            apikeyInput.value = getKey();
            apikeyInput.focus();
        }
    });
    apikeySave.addEventListener('click', () => {
        const v = apikeyInput.value.trim();
        if (v) { saveKey(v); apikeyPanel.classList.remove('open'); appendMsg('✅ API Key guardada correctamente.', 'bot'); }
    });
    apikeyInput.addEventListener('keydown', e => { if (e.key === 'Enter') apikeySave.click(); });

    // Mensajes
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

    // Llamada Gemini API (Actualizado a gemini-2.5-flash)
    async function callGemini(userMsg) {
        const key = getKey();
        if (!key) throw new Error('NO_KEY');

        history.push({ role: 'user', parts: [{ text: userMsg }] });
        if (history.length > 40) history.splice(0, 2);

        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key=${key}`;
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                system_instruction: { parts: [{ text: SYSTEM_INSTRUCTION }] },
                contents: history,
                generationConfig: { temperature: 0.4, maxOutputTokens: 1024 }
            })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            const msg = err?.error?.message || 'Error ' + res.status;
            if (res.status === 400 || res.status === 403) throw new Error('BAD_KEY:' + msg);
            throw new Error(msg);
        }

        const data = await res.json();
        const reply = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'Sin respuesta.';
        history.push({ role: 'model', parts: [{ text: reply }] });
        return reply;
    }

    // Enviar
    async function sendMessage() {
        const text = msgInput.value.trim();
        if (!text || sendBtn.disabled) return;
        appendMsg(text, 'user');
        msgInput.value = '';
        sendBtn.disabled = true;
        msgInput.disabled = true;
        showTyping();
        try {
            const reply = await callGemini(text);
            hideTyping();
            appendMsg(reply, 'bot');
        } catch(err) {
            hideTyping();
            if (err.message === 'NO_KEY') {
                apikeyPanel.classList.add('open'); apikeyInput.focus();
                appendMsg('⚙️ Ingresa tu **API Key** de Gemini en el panel de configuración (⚙️) para continuar.', 'error');
            } else if (err.message.startsWith('BAD_KEY')) {
                appendMsg('🔑 La API Key no es válida. Verifica en ⚙️ y guarda una clave correcta de [Google AI Studio](https://aistudio.google.com/apikey).', 'error');
            } else {
                appendMsg('⚠️ Error: ' + err.message, 'error');
            }
        } finally {
            sendBtn.disabled = false;
            msgInput.disabled = false;
            msgInput.focus();
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    msgInput.addEventListener('keypress', e => { if(e.key === 'Enter') sendMessage(); });
})();