/* ═══════════════════ AI 助手侧边栏逻辑 v2.1 ═══════════════════
 *  新增：快捷提问按钮、marked.js 完整 Markdown 渲染、登录状态检查
 *  作者：李康乐
 * ══════════════════════════════════════════════════════════════ */
(function () {
    'use strict';

    /* ── 登录状态检查：未登录不加载 AI 侧边栏 ── */
    var loggedInMeta = document.querySelector('meta[name="user-logged-in"]');
    if (!loggedInMeta || loggedInMeta.content !== 'true') {
        return; // 未登录，直接退出，不创建任何 UI
    }

    /* ── 全局上下文（由各页面注入） ── */
    window.AI_CONTEXT = window.AI_CONTEXT || {};

    let isOpen = false;
    let isStreaming = false;
    let messages = [];
    let markedReady = false; // marked.js 是否加载就绪

    /* ── 动态加载 marked.js ── */
    function loadMarked(cb) {
        if (typeof marked !== 'undefined') { markedReady = true; cb(); return; }
        var s = document.createElement('script');
        s.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
        s.onload = function () { markedReady = true; cb(); };
        s.onerror = function () { markedReady = false; cb(); }; // 降级
        document.head.appendChild(s);
    }

    /* ── 上下文感知的快捷提问 ── */
    function getQuickPrompts() {
        var ctx = window.AI_CONTEXT || {};
        if (ctx.operationName) {
            return [
                { label: '分析当前结果', q: '请分析当前「' + ctx.operationName + '」处理结果的特点和效果。' },
                { label: '解释这个算法', q: '请详细解释「' + ctx.operationName + '」的算法原理和数学基础。' },
                { label: '参数如何优化', q: '针对「' + ctx.operationName + '」，有哪些参数可以调节？如何优化以获得更好的效果？' },
                { label: '应用场景', q: '「' + ctx.operationName + '」在工程中有哪些典型应用场景？' }
            ];
        }
        if (ctx.chapterTitle) {
            return [
                { label: '本章要点', q: '请总结「' + ctx.chapterTitle + '」这一章的核心知识点和学习要点。' },
                { label: '算法对比', q: '请把本章涉及的主要算法进行对比，分别说明它们的优缺点和适用场景。' },
                { label: '疑难解答', q: '学习「' + ctx.chapterTitle + '」时有哪些常见的难点和理解误区？' },
                { label: '推荐学习路径', q: '学习数字图像处理，从入门到进阶的推荐学习路径是什么？' }
            ];
        }
        // 通用（章节列表 / 首页 / 对比页）
        return [
            { label: '平台有什么功能', q: '这个数字图像处理教学平台包含哪些功能和章节？请简要介绍。' },
            { label: '推荐学习路径', q: '学习数字图像处理，从入门到进阶的推荐学习路径是什么？' },
            { label: '核心概念', q: '数字图像处理中最核心的几个概念是什么？请用通俗的语言解释。' },
            { label: '入门问题', q: '我是数字图像处理的初学者，应该从哪里开始？需要什么基础？' }
        ];
    }

    /* ── 构建 DOM ── */
    function buildSidebar() {
        var prompts = getQuickPrompts();
        var promptsHTML = prompts.map(function (p) {
            return '<button class="ai-quick-btn" data-q="' + escapeAttr(p.q) + '">' + escapeHtml(p.label) + '</button>';
        }).join('');

        var toggle = document.createElement('button');
        toggle.className = 'ai-toggle-btn';
        toggle.id = 'aiToggleBtn';
        toggle.innerHTML = 'AI 助手';
        toggle.addEventListener('click', openSidebar);

        var sidebar = document.createElement('aside');
        sidebar.className = 'ai-sidebar';
        sidebar.id = 'aiSidebar';
        sidebar.innerHTML =
            '<div class="ai-sidebar-header">' +
            '<h3>' +
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
            '<path d="M12 2a3 3 0 0 1 3 3v1a3 3 0 0 1 0 6 3 3 0 0 1-6 0 3 3 0 0 1 0-6V5a3 3 0 0 1 3-3z"/>' +
            '<path d="M5 21v-2a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v2"/>' +
            '</svg>' +
            'AI 学习助手' +
            '</h3>' +
            '<button class="ai-close-btn" id="aiCloseBtn" title="收起">&times;</button>' +
            '</div>' +
            '<div class="ai-context-bar" id="aiContextBar">' +
            '<span class="ctx-dot"></span>' +
            '<span id="aiContextText">上下文：通用问答</span>' +
            '</div>' +
            '<div class="ai-quick-prompts" id="aiQuickPrompts">' + promptsHTML + '</div>' +
            '<div class="ai-chat-messages" id="aiMessages"></div>' +
            '<div class="ai-input-area">' +
            '<textarea id="aiInput" placeholder="输入你的问题，AI 将结合当前章节内容回答…" rows="1"></textarea>' +
            '<button class="ai-send-btn" id="aiSendBtn" title="发送">' +
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
            '<path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>' +
            '</svg>' +
            '</button>' +
            '</div>';

        document.body.appendChild(toggle);
        document.body.appendChild(sidebar);

        // 事件绑定
        document.getElementById('aiCloseBtn').addEventListener('click', closeSidebar);
        document.getElementById('aiSendBtn').addEventListener('click', sendMessage);
        var input = document.getElementById('aiInput');
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
        });
        input.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });

        // 快捷提问按钮
        var quickBtns = document.querySelectorAll('.ai-quick-btn');
        for (var i = 0; i < quickBtns.length; i++) {
            quickBtns[i].addEventListener('click', function () {
                var q = this.getAttribute('data-q');
                if (!isOpen) openSidebar();
                var inp = document.getElementById('aiInput');
                if (inp) { inp.value = q; sendMessage(); }
            });
        }

        // 预加载 marked.js
        loadMarked(function () { /* loaded */ });
        updateContextBar();
    }

    /* ── Markdown 渲染 ── */
    function renderMarkdown(text) {
        if (markedReady && typeof marked !== 'undefined') {
            try {
                return marked.parse(text);
            } catch (e) { /* fall back */ }
        }
        // 降级：轻量格式化
        var html = escapeHtml(text);
        html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        html = html.replace(/\n{2,}/g, '</p><p>');
        html = '<p>' + html + '</p>';
        html = html.replace(/^\s*[-*]\s+(.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>');
        return html;
    }

    /* ── 工具函数 ── */
    function escapeHtml(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
    function escapeAttr(s) {
        return s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    /* ── 上下文栏 ── */
    function updateContextBar() {
        var ctx = window.AI_CONTEXT || {};
        var parts = [];
        if (ctx.chapterTitle) parts.push(ctx.chapterTitle);
        if (ctx.operationName) parts.push('实操：' + ctx.operationName);
        var text = parts.length ? '上下文：' + parts.join(' · ') : '上下文：通用问答';
        var el = document.getElementById('aiContextText');
        if (el) el.textContent = text;
    }

    /* ── 开 / 关 ── */
    function openSidebar() {
        isOpen = true;
        document.getElementById('aiSidebar').classList.add('open');
        var toggle = document.getElementById('aiToggleBtn');
        toggle.classList.add('open-state');
        toggle.classList.add('hidden');
        var input = document.getElementById('aiInput');
        if (input) setTimeout(function () { input.focus(); }, 350);
    }
    function closeSidebar() {
        isOpen = false;
        document.getElementById('aiSidebar').classList.remove('open');
        var toggle = document.getElementById('aiToggleBtn');
        toggle.classList.remove('open-state');
        toggle.classList.remove('hidden');
    }

    function addMessage(role, content, isStreamingNode) {
        var container = document.getElementById('aiMessages');
        var msg = document.createElement('div');
        msg.className = 'ai-msg ' + role;
        if (isStreamingNode) msg.id = 'aiStreamingMsg';
        msg.innerHTML = content;
        container.appendChild(msg);
        container.scrollTop = container.scrollHeight;
        return msg;
    }

    /* ── 隐藏快捷提示（首次对话后） ── */
    function hideQuickPrompts() {
        var el = document.getElementById('aiQuickPrompts');
        if (el) el.classList.add('collapsed');
    }

    /* ── 发送消息 ── */
    async function sendMessage() {
        if (isStreaming) return;
        var input = document.getElementById('aiInput');
        var text = input.value.trim();
        if (!text) return;

        hideQuickPrompts();

        addMessage('user', escapeHtml(text));
        messages.push({ role: 'user', content: text });
        input.value = '';
        input.style.height = 'auto';

        var assistantMsg = addMessage('assistant', '<span class="typing-cursor"></span>', true);
        var streamingEl = document.getElementById('aiStreamingMsg');
        streamingEl.classList.add('typing-cursor');
        streamingEl.innerHTML = '<span class="typing-cursor"></span>';

        isStreaming = true;
        document.getElementById('aiSendBtn').disabled = true;

        try {
            var resp = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    history: messages.slice(0, -1),
                    context: window.AI_CONTEXT || {}
                })
            });

            if (!resp.ok) {
                var errData = await resp.json().catch(function () { return {}; });
                streamingEl.classList.remove('typing-cursor');
                if (resp.status === 503) {
                    showConfigOverlay(errData.message || 'AI 服务未配置');
                    streamingEl.innerHTML = '<p style="color:#e74c3c;">' + escapeHtml(errData.message || 'AI 服务未配置，请设置 DEEPSEEK_API_KEY 环境变量') + '</p>';
                } else {
                    streamingEl.innerHTML = '<p style="color:#e74c3c;">请求失败：' + escapeHtml(errData.message || resp.statusText) + '</p>';
                }
                isStreaming = false;
                document.getElementById('aiSendBtn').disabled = false;
                return;
            }

            // SSE 流式读取
            var reader = resp.body.getReader();
            var decoder = new TextDecoder();
            var fullText = '';
            streamingEl.classList.remove('typing-cursor');
            streamingEl.innerHTML = '';

            while (true) {
                var readResult = await reader.read();
                if (readResult.done) break;
                var chunk = decoder.decode(readResult.value, { stream: true });
                var lines = chunk.split('\n');
                for (var i = 0; i < lines.length; i++) {
                    var trimmed = lines[i].trim();
                    if (!trimmed.startsWith('data:')) continue;
                    var data = trimmed.slice(5).trim();
                    if (data === '[DONE]') continue;
                    try {
                        var json = JSON.parse(data);
                        var delta = json.choices && json.choices[0] && json.choices[0].delta && json.choices[0].delta.content || '';
                        if (delta) {
                            fullText += delta;
                            streamingEl.innerHTML = renderMarkdown(fullText) + '<span class="typing-cursor"></span>';
                            var container = document.getElementById('aiMessages');
                            container.scrollTop = container.scrollHeight;
                        }
                    } catch (e) { /* 忽略解析错误 */ }
                }
            }

            streamingEl.classList.remove('typing-cursor');
            streamingEl.innerHTML = renderMarkdown(fullText);
            messages.push({ role: 'assistant', content: fullText });

        } catch (err) {
            streamingEl.classList.remove('typing-cursor');
            streamingEl.innerHTML = '<p style="color:#e74c3c;">网络错误：' + escapeHtml(err.message) + '</p>';
        } finally {
            isStreaming = false;
            document.getElementById('aiSendBtn').disabled = false;
        }
    }

    /* ── 配置提示 ── */
    function showConfigOverlay(msg) {
        if (document.getElementById('aiConfigOverlay')) return;
        var overlay = document.createElement('div');
        overlay.className = 'ai-config-overlay';
        overlay.id = 'aiConfigOverlay';
        overlay.innerHTML =
            '<div class="ai-config-card">' +
            '<h3>AI 助手待配置</h3>' +
            '<p>' + escapeHtml(msg || 'AI 功能需要配置 DeepSeek API Key 才能使用。') + '<br><br>' +
            '请在启动前设置环境变量：<br><code>export DEEPSEEK_API_KEY="你的密钥"</code></p>' +
            '<button onclick="this.parentElement.parentElement.remove()">我知道了</button>' +
            '</div>';
        document.body.appendChild(overlay);
    }

    /* ── 公共 API ── */
    window.AIAssistant = {
        open: openSidebar,
        close: closeSidebar,
        ask: function (text) {
            if (!isOpen) openSidebar();
            var input = document.getElementById('aiInput');
            if (input) { input.value = text; sendMessage(); }
        },
        setContext: function (ctx) {
            window.AI_CONTEXT = Object.assign(window.AI_CONTEXT || {}, ctx);
            updateContextBar();
            // 刷新快捷提问
            refreshQuickPrompts();
        }
    };

    function refreshQuickPrompts() {
        var container = document.getElementById('aiQuickPrompts');
        if (!container) return;
        var prompts = getQuickPrompts();
        var html = '';
        for (var i = 0; i < prompts.length; i++) {
            html += '<button class="ai-quick-btn" data-q="' + escapeAttr(prompts[i].q) + '">' + escapeHtml(prompts[i].label) + '</button>';
        }
        container.innerHTML = html;
        container.classList.remove('collapsed');
        var btns = container.querySelectorAll('.ai-quick-btn');
        for (var j = 0; j < btns.length; j++) {
            btns[j].addEventListener('click', function () {
                var q = this.getAttribute('data-q');
                if (!isOpen) openSidebar();
                var inp = document.getElementById('aiInput');
                if (inp) { inp.value = q; sendMessage(); }
            });
        }
    }

    /* ── 初始化 ── */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', buildSidebar);
    } else {
        buildSidebar();
    }
})();
