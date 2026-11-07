// ===== 小哨吉祥物 SVG (蓝色小企鹅) =====
const MASCOT_SVG = `
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <radialGradient id="bodyGrad" cx="35%" cy="30%" r="65%">
            <stop offset="0%" stop-color="#7eb8ff"/>
            <stop offset="60%" stop-color="#5ba3f5"/>
            <stop offset="100%" stop-color="#4a90d9"/>
        </radialGradient>
        <radialGradient id="bellyGrad" cx="40%" cy="35%" r="60%">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="70%" stop-color="#f5f8ff"/>
            <stop offset="100%" stop-color="#e0e8f5"/>
        </radialGradient>
        <radialGradient id="starGrad" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stop-color="#ffe566"/>
            <stop offset="50%" stop-color="#ffd700"/>
            <stop offset="100%" stop-color="#f5c200"/>
        </radialGradient>
        <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="1.5" result="blur"/>
            <feOffset dx="0" dy="1" result="offset"/>
            <feComposite in="SourceGraphic" in2="offset" operator="over"/>
        </filter>
    </defs>
    <!-- 天使光环 -->
    <ellipse cx="50" cy="14" rx="16" ry="4" fill="none" stroke="#a8d8ff" stroke-width="2.5" opacity="0.85"/>
    <ellipse cx="50" cy="13" rx="16" ry="4" fill="none" stroke="#c8e8ff" stroke-width="1" opacity="0.5"/>
    <!-- 身体 -->
    <ellipse cx="50" cy="58" rx="30" ry="34" fill="url(#bodyGrad)"/>
    <!-- 白色肚子 -->
    <ellipse cx="50" cy="64" rx="20" ry="24" fill="url(#bellyGrad)"/>
    <!-- 黄色五角星 -->
    <polygon points="50,52 53,59 60,59 54.5,63.5 56.5,70.5 50,66.5 43.5,70.5 45.5,63.5 40,59 47,59" fill="url(#starGrad)" stroke="#e6b800" stroke-width="0.5"/>
    <!-- 星星笑脸 -->
    <circle cx="47.5" cy="62" r="1" fill="#8b6914"/>
    <circle cx="52.5" cy="62" r="1" fill="#8b6914"/>
    <path d="M48,64 Q50,65.5 52,64" stroke="#8b6914" stroke-width="0.6" fill="none" stroke-linecap="round"/>
    <!-- 左眼白 -->
    <ellipse cx="40" cy="38" rx="9" ry="10" fill="white"/>
    <!-- 右眼白 -->
    <ellipse cx="60" cy="38" rx="9" ry="10" fill="white"/>
    <!-- 左瞳孔 -->
    <circle cx="40" cy="39" r="4.5" fill="#2a2a2a" class="eye-left"/>
    <!-- 右瞳孔 -->
    <circle cx="60" cy="39" r="4.5" fill="#2a2a2a" class="eye-right"/>
    <!-- 左眼高光 -->
    <circle cx="38.5" cy="36.5" r="1.6" fill="white" opacity="0.9"/>
    <!-- 右眼高光 -->
    <circle cx="58.5" cy="36.5" r="1.6" fill="white" opacity="0.9"/>
    <!-- 小嘴巴 -->
    <ellipse cx="50" cy="49" rx="5.5" ry="3" fill="#ff9f43"/>
    <ellipse cx="50" cy="48.5" rx="4" ry="1.5" fill="#ffb366" opacity="0.5"/>
    <!-- 左腮红 -->
    <ellipse cx="32" cy="46" rx="5" ry="3.5" fill="#ffb3b3" opacity="0.45"/>
    <!-- 右腮红 -->
    <ellipse cx="68" cy="46" rx="5" ry="3.5" fill="#ffb3b3" opacity="0.45"/>
    <!-- 左翅膀 -->
    <ellipse cx="18" cy="58" rx="7" ry="14" fill="#4a8ee0" transform="rotate(-15 18 58)"/>
    <!-- 右翅膀 -->
    <ellipse cx="82" cy="58" rx="7" ry="14" fill="#4a8ee0" transform="rotate(15 82 58)"/>
    <!-- 左脚 -->
    <ellipse cx="40" cy="91" rx="8" ry="4.5" fill="#ff9f43"/>
    <ellipse cx="40" cy="90" rx="5" ry="2" fill="#ffb366" opacity="0.4"/>
    <!-- 右脚 -->
    <ellipse cx="60" cy="91" rx="8" ry="4.5" fill="#ff9f43"/>
    <ellipse cx="60" cy="90" rx="5" ry="2" fill="#ffb366" opacity="0.4"/>
</svg>`;

const MASCOT_THINKING_SVG = MASCOT_SVG.replace(
    '<svg viewBox="0 0 100 100"',
    '<svg viewBox="0 0 100 100" class="mascot-bounce"'
);

// 默认用户头像
const DEFAULT_AVATAR_SVG = `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <defs><linearGradient id="avG" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#f093fb"/><stop offset="100%" stop-color="#f5576c"/>
    </linearGradient></defs>
    <circle cx="50" cy="50" r="50" fill="url(#avG)"/>
    <circle cx="50" cy="38" r="15" fill="white" opacity="0.95"/>
    <path d="M25 82 Q25 58 50 58 Q75 58 75 82 Z" fill="white" opacity="0.95"/>
</svg>`;

// 眼睛基础坐标(适配新吉祥物眼睛位置)
const EYE_BASE = { lx: 40, ly: 39, rx: 60, ry: 39 };

// ===== DOM 引用 =====
const chatArea = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
let isTyping = false;

// ===== 吉祥物初始化 =====
function initMascots() {
    document.getElementById('headerMascot').innerHTML = MASCOT_SVG;
    document.getElementById('welcomeMascot').innerHTML = MASCOT_SVG;
    // 仅顶部栏吉祥物有点击互动
    document.getElementById('headerMascot').addEventListener('click', function() {
        playMascotAnim(this);
    });
    // 启动待机动画(随机触发旋转/摇摆/歪头)
    startIdleAnimations();
}

// ===== 顶部栏吉祥物待机动画(随机触发) =====
let idleAnimTimer = null;

function startIdleAnimations() {
    function scheduleNext() {
        const delay = 6000 + Math.random() * 6000; // 6-12秒随机间隔
        idleAnimTimer = setTimeout(function() {
            playIdleAnim();
            scheduleNext();
        }, delay);
    }
    scheduleNext();
}

function playIdleAnim() {
    const container = document.getElementById('headerMascot');
    if (!container) return;
    const svg = container.querySelector('svg');
    if (!svg) return;

    const pool = ['rotate', 'wiggle', 'tilt'];
    const anim = pool[Math.floor(Math.random() * pool.length)];
    const cls = 'mascot-idle-' + anim;

    // 移除之前的待机动画类
    svg.classList.remove('mascot-idle-rotate', 'mascot-idle-wiggle', 'mascot-idle-tilt');
    void svg.offsetWidth; // 强制重绘
    svg.classList.add(cls);

    // 动画结束后移除类
    const duration = anim === 'tilt' ? 1500 : (anim === 'rotate' ? 1200 : 900);
    setTimeout(function() {
        svg.classList.remove(cls);
    }, duration);
}

function getBotAvatar() {
    return `<div class="bot-avatar">${MASCOT_SVG}</div>`;
}

function getThinkingHTML() {
    return `
        <div class="thinking" id="thinkingMsg">
            <div class="bot-avatar">${MASCOT_THINKING_SVG}</div>
            <div class="thinking-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
}

// ===== 眼睛追随鼠标 =====
let mouseX = 0, mouseY = 0, eyeRAF = null;

document.addEventListener('mousemove', function(e) {
    mouseX = e.clientX;
    mouseY = e.clientY;
    if (!eyeRAF) eyeRAF = requestAnimationFrame(updateEyeTracking);
});

function updateEyeTracking() {
    eyeRAF = null;
    ['headerMascot'].forEach(function(id) {
        const el = document.getElementById(id);
        if (!el || el.offsetParent === null) return;
        const svg = el.querySelector('svg');
        if (!svg) return;
        const lp = svg.querySelector('.eye-left');
        const rp = svg.querySelector('.eye-right');
        if (!lp || !rp) return;
        const rect = el.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height * 0.38;
        const dx = mouseX - cx;
        const dy = mouseY - cy;
        const angle = Math.atan2(dy, dx);
        const dist = Math.min(2.5, Math.hypot(dx, dy) / 30);
        const ox = Math.cos(angle) * dist;
        const oy = Math.sin(angle) * dist;
        lp.setAttribute('cx', EYE_BASE.lx + ox);
        lp.setAttribute('cy', EYE_BASE.ly + oy);
        rp.setAttribute('cx', EYE_BASE.rx + ox);
        rp.setAttribute('cy', EYE_BASE.ry + oy);
    });
}

// ===== 点击吉祥物动画 =====
function playMascotAnim(container) {
    const pool = ['hearts', 'jump', 'hearts', 'spin', 'hearts'];
    const anim = pool[Math.floor(Math.random() * pool.length)];
    const svg = container.querySelector('svg');
    if (anim === 'spin' && svg) {
        svg.classList.remove('mascot-spin');
        void svg.offsetWidth;
        svg.classList.add('mascot-spin');
        setTimeout(function() { svg.classList.remove('mascot-spin'); }, 750);
    } else if (anim === 'jump') {
        container.classList.remove('mascot-jump');
        void container.offsetWidth;
        container.classList.add('mascot-jump');
        setTimeout(function() { container.classList.remove('mascot-jump'); }, 750);
    } else if (anim === 'hearts') {
        spawnHearts(container);
        container.classList.remove('mascot-jump');
        void container.offsetWidth;
        container.classList.add('mascot-jump');
        setTimeout(function() { container.classList.remove('mascot-jump'); }, 750);
    }
}

function spawnHearts(container) {
    const rect = container.getBoundingClientRect();
    const hearts = ['❤️', '💖', '💕', '💗', '💓'];
    const count = 4 + Math.floor(Math.random() * 3);
    for (let i = 0; i < count; i++) {
        const h = document.createElement('div');
        h.className = 'floating-heart';
        h.textContent = hearts[Math.floor(Math.random() * hearts.length)];
        h.style.left = (rect.left + rect.width / 2 + (Math.random() - 0.5) * rect.width) + 'px';
        h.style.top = (rect.top + rect.height * 0.3) + 'px';
        h.style.animationDelay = (i * 0.12) + 's';
        h.style.fontSize = (14 + Math.random() * 10) + 'px';
        document.body.appendChild(h);
        setTimeout(function() { h.remove(); }, 1800);
    }
}

// ===== 用户头像 =====
function getUserAvatarHTML() {
    const saved = localStorage.getItem('userAvatar');
    if (saved) return `<img src="${saved}" alt="我">`;
    return DEFAULT_AVATAR_SVG;
}

function refreshUserAvatars() {
    const headerAv = document.getElementById('userAvatarBtn');
    if (headerAv) headerAv.innerHTML = getUserAvatarHTML();
    const settingsAv = document.getElementById('settingsAvatar');
    if (settingsAv) settingsAv.innerHTML = getUserAvatarHTML();
    document.querySelectorAll('.message.user .user-avatar').forEach(function(el) {
        el.innerHTML = getUserAvatarHTML();
    });
}

function handleAvatarUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(ev) {
        const img = new Image();
        img.onload = function() {
            const canvas = document.createElement('canvas');
            const size = 120;
            canvas.width = size;
            canvas.height = size;
            const ctx = canvas.getContext('2d');
            const min = Math.min(img.width, img.height);
            const sx = (img.width - min) / 2;
            const sy = (img.height - min) / 2;
            ctx.drawImage(img, sx, sy, min, min, 0, 0, size, size);
            try {
                localStorage.setItem('userAvatar', canvas.toDataURL('image/png'));
            } catch (err) {
                alert('保存失败,图片可能过大。');
                return;
            }
            refreshUserAvatars();
        };
        img.src = ev.target.result;
    };
    reader.readAsDataURL(file);
    e.target.value = '';
}

function resetAvatar() {
    localStorage.removeItem('userAvatar');
    refreshUserAvatars();
}

// ===== 对话背景 =====
function applyBackground() {
    const bg = localStorage.getItem('chatBg');
    if (bg) {
        chatArea.style.backgroundImage = 'url(' + bg + ')';
    } else {
        chatArea.style.backgroundImage = '';
    }
}

function handleBgUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(ev) {
        const img = new Image();
        img.onload = function() {
            const canvas = document.createElement('canvas');
            const maxSide = 1000;
            let w = img.width, h = img.height;
            if (w > maxSide || h > maxSide) {
                if (w > h) { h = Math.round(h * maxSide / w); w = maxSide; }
                else { w = Math.round(w * maxSide / h); h = maxSide; }
            }
            canvas.width = w;
            canvas.height = h;
            canvas.getContext('2d').drawImage(img, 0, 0, w, h);
            try {
                localStorage.setItem('chatBg', canvas.toDataURL('image/jpeg', 0.8));
            } catch (err) {
                alert('图片过大,无法保存,请选择较小的图片。');
                return;
            }
            applyBackground();
        };
        img.src = ev.target.result;
    };
    reader.readAsDataURL(file);
    e.target.value = '';
}

function resetBackground() {
    localStorage.removeItem('chatBg');
    applyBackground();
}

// ===== 主题切换 =====
function setTheme(theme) {
    document.getElementById('app').className = 'app theme-' + theme;
    localStorage.setItem('theme', theme);
    document.querySelectorAll('.theme-btn').forEach(function(btn) {
        btn.classList.toggle('active', btn.dataset.theme === theme);
    });
}

function initTheme() {
    const saved = localStorage.getItem('theme') || 'blue';
    setTheme(saved);
}

// ===== 设置弹窗 =====
function openSettings() {
    document.getElementById('settingsOverlay').classList.add('active');
}

function closeSettings() {
    document.getElementById('settingsOverlay').classList.remove('active');
}

// 点击遮罩关闭弹窗
document.getElementById('settingsOverlay').addEventListener('click', function(e) {
    if (e.target === this) closeSettings();
});

// 主题按钮点击
document.querySelectorAll('.theme-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
        setTheme(this.dataset.theme);
    });
});

// 头像上传监听
document.getElementById('avatarInput').addEventListener('change', handleAvatarUpload);
document.getElementById('bgInput').addEventListener('change', handleBgUpload);

// ===== 分享功能 =====
let shareUrl = '';

function openShare() {
    document.getElementById('shareOverlay').classList.add('active');
    loadShareInfo();
}

function closeShare() {
    document.getElementById('shareOverlay').classList.remove('active');
}

document.getElementById('shareOverlay').addEventListener('click', function(e) {
    if (e.target === this) closeShare();
});

async function loadShareInfo() {
    const qrEl = document.getElementById('qrcode');
    const hintEl = document.getElementById('qrHint');
    const urlEl = document.getElementById('shareUrl');
    qrEl.innerHTML = '';
    hintEl.textContent = '正在获取地址...';
    urlEl.textContent = '获取中...';
    try {
        const res = await fetch('/api/network-info');
        const data = await res.json();
        if (data.urls && data.urls.length > 0) {
            shareUrl = data.urls[0];
            urlEl.textContent = shareUrl;
            hintEl.textContent = '手机扫码即可打开';
            if (typeof QRCode !== 'undefined') {
                new QRCode(qrEl, {
                    text: shareUrl,
                    width: 180,
                    height: 180,
                    colorDark: '#333',
                    colorLight: '#ffffff',
                    correctLevel: QRCode.CorrectLevel.M
                });
            } else {
                hintEl.textContent = '二维码库加载失败,请手动复制地址';
            }
        } else {
            hintEl.textContent = '未检测到局域网IP,请手动告知对方本机IP+端口5000';
            urlEl.textContent = '未检测到可用地址';
        }
    } catch (err) {
        hintEl.textContent = '获取失败,请检查服务是否正常运行';
        urlEl.textContent = '获取失败';
    }
}

function copyShareUrl() {
    if (!shareUrl) return;
    if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl).then(function() {
            showToast('已复制到剪贴板!');
        });
    } else {
        // 兼容旧浏览器
        const ta = document.createElement('textarea');
        ta.value = shareUrl;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast('已复制到剪贴板!');
    }
}

function showToast(msg) {
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function() { t.remove(); }, 2000);
}

// 顶部头像点击更换
document.getElementById('userAvatarBtn').addEventListener('click', function() {
    document.getElementById('avatarInput').click();
});

// ===== 输入处理 =====
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function scrollToBottom() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'message user';
    div.innerHTML = '<div class="bubble">' + escapeHtml(text) + '</div><div class="user-avatar">' + getUserAvatarHTML() + '</div>';
    chatArea.appendChild(div);
    scrollToBottom();
}

function addBotMessage(text) {
    const div = document.createElement('div');
    div.className = 'message bot';
    const formatted = escapeHtml(text)
        .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
        .replace(/\n/g, '<br>');
    div.innerHTML = getBotAvatar() + '<div class="bubble">' + formatted + '</div>';
    chatArea.appendChild(div);
    scrollToBottom();
}

function showThinking() {
    const div = document.createElement('div');
    div.innerHTML = getThinkingHTML();
    chatArea.appendChild(div.firstElementChild);
    scrollToBottom();
}

function hideThinking() {
    const el = document.getElementById('thinkingMsg');
    if (el) el.remove();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text || isTyping) return;

    // 模拟演练模式:消息发送给演练对话
    if (roleplayActive) {
        userInput.value = '';
        userInput.style.height = 'auto';
        sendRoleplayMessage(text);
        return;
    }

    userInput.value = '';
    userInput.style.height = 'auto';

    addUserMessage(text);

    const localReply = handleLocalCommand(text);
    if (localReply !== null) {
        if (localReply === '__EXIT__') {
            addBotMessage('👋 再见!不轻信、不转账、不透露验证码!');
            return;
        }
        addBotMessage(localReply);
        return;
    }

    isTyping = true;
    sendBtn.disabled = true;
    showThinking();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, session_id: 'web' })
        });
        const data = await res.json();
        hideThinking();
        if (data.error) {
            addBotMessage('⚠️ 出错了:' + data.error);
        } else {
            addBotMessage(data.reply);
        }
    } catch (err) {
        hideThinking();
        addBotMessage('⚠️ 网络连接失败,请检查服务是否运行。紧急情况请拨打 110 / 96110!');
    } finally {
        isTyping = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function handleLocalCommand(text) {
    const cmd = text.toLowerCase();
    if (cmd === '帮助' || cmd === 'help' || cmd === 'h' || cmd === '?') {
        return `📖 **小哨功能说明书**

🛡️ **小哨是谁?**
你的校园反诈小卫士,覆盖**冒、利、恐、贷、交、学**6大诈骗套路全防护!

━━━━━━━━━━━━━━
🎯 **场景互动答题**
点底部「🎯 场景互动」→ 选套路分类 → 挑具体场景 → 开始挑战!
每个场景随机生成不同故事分支,在答题中学会识破骗局。
6大分类:冒(冒充身份) 利(利诱贪心) 恐(恐吓胁迫) 贷(虚假借贷) 交(虚假交易) 学(学业骗局)

🎭 **骗子模拟演练**
点底部「🎭 模拟演练」→ 选套路 → 挑骗子角色 → 实时对话!
小哨扮演骗子用真实话术与你过招,在安全环境训练防骗反应。
每次随机生成不同骗子形象,结束后给出复盘点评!

📰 **真实案例学习**
点底部「📰 真实案例」→ 选诈骗类型 → 查看近期真实案例!
案例来自新闻报道和警方通报,一次展示一个不重复,从他人教训中学习。

🔍 **反诈雷达查询**
点底部「🔍 反诈雷达」→ 输入手机号/网址/APP名称 → 即刻查询!
帮你识别已知高风险诈骗源,还能查看本周高发诈骗预警。

📎 **证据分析报案**
点底部「📎 证据分析」→ 描述情况或粘贴聊天记录 → 开始分析!
小哨自动:检测诈骗话术 → 识别诈骗类型 → 生成报案草稿 → 追问缺失细节
完成后还有🐧PPT讲解+柔和语音为你逐页解读!

💬 **智能对话**
直接在输入框描述可疑场景,小哨立刻帮你分析风险、给出防范建议。

━━━━━━━━━━━━━━
⌨️ **快捷命令**
「帮助」查看本说明
「类型」查看12种常见诈骗类型
「紧急」查看报警电话
「清空」重置对话
「退出」结束对话

🚨 **紧急联系**
报警电话 110 | 全国反诈专线 96110
推荐安装:国家反诈中心APP

━━━━━━━━━━━━━━
💡 记住:不轻信、不转账、不透露验证码!`;
    }
    if (cmd === '退出' || cmd === 'quit' || cmd === 'exit' || cmd === 'q') {
        return '__EXIT__';
    }
    if (cmd === '清空' || cmd === '重置' || cmd === 'reset') {
        resetChat();
        return '🔄 对话已清空!';
    }
    if (cmd === '类型' || cmd === '列表' || cmd === 'types') {
        return `📚 常见诈骗类型:
1. 刷单返利诈骗
2. 校园贷/注销校园贷诈骗
3. 冒充电商客服退款诈骗
4. 冒充熟人/老师/领导诈骗
5. 助学金/奖学金诈骗
6. 网络交友诱导投资(杀猪盘)
7. 游戏账号/装备交易诈骗
8. 冒充公检法诈骗
9. 演唱会/门票诈骗
10. 虚假招聘/培训贷诈骗
11. 屏幕共享/验证码诈骗
12. 虚假中奖/抽奖诈骗`;
    }
    if (cmd === '紧急' || cmd === '电话' || cmd === 'emergency') {
        return `🚨 紧急联系方式:
• 报警电话: 110
• 全国反诈专线: 96110
• 推荐安装: 国家反诈中心APP`;
    }
    return null;
}

async function resetChat() {
    try {
        await fetch('/api/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: 'web' })
        });
    } catch (e) {}
    const welcome = chatArea.querySelector('.welcome-msg');
    chatArea.innerHTML = '';
    if (welcome) chatArea.appendChild(welcome);
    userInput.focus();
}

// ===== 模块互斥:点击新模块自动退出上一个 =====
let activeModule = null; // 'quiz' | 'case' | 'radar' | 'roleplay' | 'evidence' | null

function switchModule(newModule) {
    if (activeModule === newModule) return false;
    // 退出上一个模块
    if (activeModule === 'quiz' && typeof quitQuiz === 'function') quitQuiz(true);
    else if (activeModule === 'case' && typeof quitCase === 'function') quitCase(true);
    else if (activeModule === 'radar' && typeof quitRadar === 'function') quitRadar(true);
    else if (activeModule === 'roleplay' && typeof endRoleplay === 'function') endRoleplay(true);
    else if (activeModule === 'evidence' && typeof quitEvidence === 'function') quitEvidence(true);
    activeModule = newModule;
    return true;
}

// ===== 反诈场景互动(题库数据在 quiz_data.js 中)=====
// ===== 反诈场景互动状态 =====
let quizActive = false;
let quizQuestions = [];
let quizIndex = 0;
let quizScore = 0;
let quizShuffled = []; // 当前题打乱后的选项(存原始索引)
let lastQuizPick = {}; // 记录每类上次选的分支索引,避免连续重复 { typeId: index }
let quizSessionId = 0; // 测验会话ID,防止旧setTimeout干扰新测验

function startQuizSelect() {
    if (quizActive) return;
    switchModule('quiz');
    const div = document.createElement('div');
    div.className = 'message bot';
    let cards = '';
    QUIZ_CATEGORIES.forEach(function(cat) {
        cards += '<button class="quiz-type-card" onclick="showCategoryScenes(\'' + cat.id + '\')">' +
            '<span class="quiz-type-icon">' + cat.icon + '</span>' +
            '<span class="quiz-type-name">' + cat.name + '</span>' +
            '<span class="quiz-type-desc">' + cat.desc + '</span></button>';
    });
    div.innerHTML = getBotAvatar() +
        '<div class="bubble"><b>🎯 反诈场景互动</b><br>' +
        '按<b>6大诈骗套路</b>分类挑战:<b>冒、利、恐、贷、交、学</b><br>' +
        '<span style="font-size:11px;opacity:0.7">冒=冒充身份 利=利诱贪心 恐=恐吓胁迫 贷=虚假借贷 交=虚假交易 学=学业骗局</span><br><br>' +
        '<div class="quiz-type-grid">' + cards + '</div>' +
        '<span style="font-size:12px;opacity:0.6">选择一个套路分类,再挑具体场景开始挑战!每个场景随机生成不同故事分支~</span></div>';
    chatArea.appendChild(div);
    scrollToBottom();
}

// 获取场景信息(兼容旧QUIZ_TYPES和新QUIZ_SCENES)
function getSceneInfo(sceneId) {
    if (typeof QUIZ_TYPES !== 'undefined') {
        const t = QUIZ_TYPES.find(function(x) { return x.id === sceneId; });
        if (t) return t;
    }
    if (typeof QUIZ_SCENES !== 'undefined') {
        for (const catId in QUIZ_SCENES) {
            const s = QUIZ_SCENES[catId].find(function(x) { return x.id === sceneId; });
            if (s) return s;
        }
    }
    return null;
}

// 获取场景题库数据(兼容QUIZ_DATA和QUIZ_NEW_SCENES)
function getSceneData(sceneId) {
    if (typeof QUIZ_DATA !== 'undefined' && QUIZ_DATA[sceneId]) return QUIZ_DATA[sceneId];
    if (typeof QUIZ_NEW_SCENES !== 'undefined' && QUIZ_NEW_SCENES[sceneId]) return QUIZ_NEW_SCENES[sceneId];
    return null;
}

// 第二级:显示某大类下的子场景
function showCategoryScenes(catId) {
    const cat = QUIZ_CATEGORIES.find(function(c) { return c.id === catId; });
    if (!cat) return;
    const scenes = QUIZ_SCENES[catId] || [];

    const div = document.createElement('div');
    div.className = 'message bot';
    let cards = '';
    scenes.forEach(function(s) {
        cards += '<button class="quiz-type-card" onclick="startQuiz(\'' + s.id + '\')">' +
            '<span class="quiz-type-icon">' + s.icon + '</span>' +
            '<span class="quiz-type-name">' + s.name + '</span>' +
            '<span class="quiz-type-desc">' + s.desc + '</span></button>';
    });
    // 随机来一个按钮
    cards += '<button class="quiz-type-card" onclick="startRandomScene(\'' + catId + '\')" style="border-color:var(--input-focus)">' +
        '<span class="quiz-type-icon">🎲</span>' +
        '<span class="quiz-type-name">随机来一个</span>' +
        '<span class="quiz-type-desc">随机选一个场景</span></button>';
    div.innerHTML = getBotAvatar() +
        '<div class="bubble"><b>' + cat.icon + ' ' + cat.name + '</b><br>' +
        '<span style="font-size:12px;opacity:0.7">' + cat.slogan + '</span><br><br>' +
        '<div class="quiz-type-grid">' + cards + '</div>' +
        '<span style="font-size:12px;opacity:0.6">选择一个具体场景,或点「🎲 随机来一个」!</span></div>';
    chatArea.appendChild(div);
    scrollToBottom();
}

// 随机选一个子场景
function startRandomScene(catId) {
    const scenes = QUIZ_SCENES[catId] || [];
    if (scenes.length === 0) return;
    const scene = scenes[Math.floor(Math.random() * scenes.length)];
    startQuiz(scene.id);
}

function startQuiz(typeId) {
    const typeInfo = getSceneInfo(typeId);
    if (!typeInfo) return;
    const sceneData = getSceneData(typeId);
    if (!sceneData) return;

    // 防重入:如果正在答题,先静默退出旧测验
    if (quizActive) quitQuiz(true);
    // 递增会话ID,使旧测验的setTimeout回调全部失效
    quizSessionId++;
    // 禁用页面上所有残留的测验选项按钮(防止点到旧题目)
    document.querySelectorAll('.quiz-option-btn:not(:disabled)').forEach(function(b) { b.disabled = true; });

    // 构建场景池:主线故事 + 分支变体
    let pool = [{ name: '经典场景', intro: typeInfo.intro || typeInfo.desc, questions: sceneData.slice(0, 10) }];
    if (typeof QUIZ_BRANCHES !== 'undefined' && QUIZ_BRANCHES[typeId]) {
        QUIZ_BRANCHES[typeId].forEach(function(b) {
            pool.push({ name: b.name, intro: b.intro, questions: b.questions });
        });
    }
    if (typeof QUIZ_NEW_BRANCHES !== 'undefined' && QUIZ_NEW_BRANCHES[typeId]) {
        QUIZ_NEW_BRANCHES[typeId].forEach(function(b) {
            pool.push({ name: b.name, intro: b.intro, questions: b.questions });
        });
    }

    // 排除上次选的分支,确保连续两次不重复
    const lastIdx = lastQuizPick[typeId];
    let candidates = pool.map(function(_, i) { return i; });
    if (typeof lastIdx === 'number' && pool.length > 1) {
        candidates = candidates.filter(function(i) { return i !== lastIdx; });
    }
    const pickIdx = candidates[Math.floor(Math.random() * candidates.length)];
    lastQuizPick[typeId] = pickIdx;
    const picked = pool[pickIdx];
    quizQuestions = picked.questions;
    quizIndex = 0;
    quizScore = 0;
    quizActive = true;

    // 显示场景介绍
    const intro = document.createElement('div');
    intro.className = 'message bot';
    intro.innerHTML = getBotAvatar() +
        '<div class="bubble"><b>' + typeInfo.icon + ' ' + typeInfo.name + ' · ' + escapeHtml(picked.name) + '</b><br><br>' +
        '<div class="quiz-scenario-intro">' + escapeHtml(picked.intro) + '</div>' +
        '<br><span style="font-size:12px;opacity:0.6">共' + quizQuestions.length + '题,准备好了吗?第一题马上来~</span></div>';
    chatArea.appendChild(intro);
    scrollToBottom();

    const sid = quizSessionId;
    setTimeout(function() { if (sid === quizSessionId) showQuizQuestion(); }, 800);
}

// 打乱数组(Fisher-Yates)
function shuffleArr(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        const tmp = a[i]; a[i] = a[j]; a[j] = tmp;
    }
    return a;
}

function showQuizQuestion() {
    if (!quizActive) return; // 测验已退出,忽略残留回调
    if (quizIndex >= quizQuestions.length) { showQuizResult(); return; }
    const q = quizQuestions[quizIndex];
    const pct = Math.round(quizIndex / quizQuestions.length * 100);

    // 进度条
    const progress = document.createElement('div');
    progress.className = 'quiz-progress';
    progress.innerHTML = '<span class="quiz-progress-text">第 ' + (quizIndex + 1) + '/' + quizQuestions.length + ' 题</span>' +
        '<div class="quiz-progress-bar"><div class="quiz-progress-fill" style="width:' + pct + '%"></div></div>' +
        '<span class="quiz-score-text">得分 ' + quizScore + '</span>' +
        '<button class="quiz-quit-btn" onclick="quitQuiz()">退出</button>';
    chatArea.appendChild(progress);

    // 打乱选项顺序
    const optIndices = q.opts.map(function(_, i) { return i; });
    quizShuffled = shuffleArr(optIndices);

    // 题目(含场景描述和对话)
    const div = document.createElement('div');
    div.className = 'message bot';
    let html = '<div class="bubble">';
    // 场景描述
    if (q.scenario) {
        html += '<div class="quiz-scenario">' + escapeHtml(q.scenario) + '</div>';
    }
    // 骗子对话
    if (q.dialogue) {
        html += '<div class="quiz-dialogue">' + escapeHtml(q.dialogue) + '</div>';
    }
    // 问题
    html += '<div class="quiz-question"><b>' + escapeHtml(q.q) + '</b></div>';
    // 选项(打乱后)
    html += '<div class="quiz-options">';
    quizShuffled.forEach(function(origIdx, displayIdx) {
        html += '<button class="quiz-option-btn" onclick="answerQuiz(' + origIdx + ')">' +
            String.fromCharCode(65 + displayIdx) + '. ' + escapeHtml(q.opts[origIdx]) + '</button>';
    });
    html += '</div></div>';
    div.innerHTML = getBotAvatar() + html;
    chatArea.appendChild(div);
    scrollToBottom();
}

function answerQuiz(choice) {
    if (!quizActive) return; // 测验已退出,忽略旧按钮点击
    const q = quizQuestions[quizIndex];
    if (!q) return;
    // 找到打乱后正确答案的显示位置
    const correctDisplayIdx = quizShuffled.indexOf(q.a);
    const choiceDisplayIdx = quizShuffled.indexOf(choice);
    // 只处理当前题的按钮(页面上最后出现的一组未禁用按钮)
    const allBtns = document.querySelectorAll('.quiz-option-btn:not(:disabled)');
    const currentBtns = Array.from(allBtns).slice(-q.opts.length);
    currentBtns.forEach(function(b, i) {
        b.disabled = true;
        if (i === correctDisplayIdx) b.classList.add('correct');
        if (i === choiceDisplayIdx && choice !== q.a) b.classList.add('wrong');
    });
    const correct = choice === q.a;
    if (correct) quizScore += 10;

    // 解析
    const exp = document.createElement('div');
    exp.className = 'message bot';
    exp.innerHTML = getBotAvatar() +
        '<div class="bubble">' + (correct ? '✅ <b>回答正确!</b>' : '❌ <b>回答错误!</b> 正确答案是 ' + String.fromCharCode(65 + correctDisplayIdx) + '. ' + escapeHtml(q.opts[q.a]) + '<br>') +
        '<br>💡 ' + escapeHtml(q.exp) + '</div>';
    chatArea.appendChild(exp);
    scrollToBottom();

    quizIndex++;
    const sid = quizSessionId;
    setTimeout(function() { if (sid === quizSessionId) showQuizQuestion(); }, 1500);
}

function showQuizResult() {
    quizActive = false;

    let badge, color, comment;
    if (quizScore >= 90) {
        badge = '🏆 反诈达人'; color = '#ffd700';
        comment = '太棒了!你的防骗意识非常强,各种诈骗套路都骗不到你!继续保持警惕,也记得提醒身边的同学朋友,让更多人远离诈骗!';
    } else if (quizScore >= 70) {
        badge = '🥈 防骗高手'; color = '#c0c0c0';
        comment = '不错!你对常见诈骗手法有较好的认知。不过还有少数套路可能让你中招,建议多关注反诈知识,遇到拿不准的情况随时来问小哨!';
    } else if (quizScore >= 50) {
        badge = '🛡️ 尚需努力'; color = '#cd7f32';
        comment = '你的防骗意识还有提升空间。记住三条铁律:不轻信、不转账、不透露验证码!建议把答错的题目解析再看看,巩固薄弱环节。';
    } else {
        badge = '⚠️ 需要充电'; color = '#ff4d4f';
        comment = '你的防骗意识比较薄弱,很容易被骗子盯上!强烈建议:1️⃣ 立即安装"国家反诈中心"APP;2️⃣ 牢记"三不一多":不轻信、不透露、不转账,多核实;3️⃣ 遇到可疑情况随时问小哨或拨打96110!';
    }

    const div = document.createElement('div');
    div.className = 'message bot';
    div.innerHTML = getBotAvatar() +
        '<div class="bubble"><div class="quiz-result">' +
        '<div class="quiz-result-label">挑战结束!你的成绩是</div>' +
        '<div class="quiz-result-score" style="color:' + color + '">' + quizScore + '<span style="font-size:20px">分</span></div>' +
        '<span class="quiz-result-badge" style="background:' + color + '22;color:' + color + '">' + badge + '</span>' +
        '<div class="quiz-result-comment">' + comment + '</div>' +
        '<div class="quiz-result-actions">' +
        '<button class="settings-action-btn" onclick="startQuizSelect()">🎯 再来一轮</button>' +
        '</div></div></div>';
    chatArea.appendChild(div);
    scrollToBottom();
}

function quitQuiz(silent) {
    quizActive = false;
    quizQuestions = [];
    quizSessionId++; // 使残留的setTimeout回调全部失效
    // 禁用页面上所有残留的测验选项按钮
    document.querySelectorAll('.quiz-option-btn:not(:disabled)').forEach(function(b) { b.disabled = true; });
    if (activeModule === 'quiz') activeModule = null;
    if (!silent) addBotMessage('👋 已退出场景互动。你的得分:' + quizScore + ' 分。想继续挑战随时点「🎯 反诈场景互动」!');
}

// ===== 真实案例分享 =====
let caseActive = false;
let caseSeenTitles = {}; // { categoryId: [titles...] }

const CASE_TYPES = [
    { id: 'maochong', name: '冒充类', icon: '🎭', desc: '冒充客服/熟人/公检法' },
    { id: 'liyou',    name: '利诱类', icon: '💰', desc: '刷单返利/杀猪盘' },
    { id: 'jiaoyi',   name: '交易类', icon: '🛒', desc: '游戏交易/二手交易' },
    { id: 'xiepo',    name: '恐吓类', icon: '⚠️', desc: '公检法恐吓/征信修复' },
    { id: 'xueye',    name: '学业类', icon: '🎓', desc: '考试保过/助学金' },
    { id: 'jiedai',   name: '借贷类', icon: '🏦', desc: '校园贷/培训贷' },
];

function startCaseSelect() {
    if (caseActive) return;
    switchModule('case');
    const div = document.createElement('div');
    div.className = 'message bot';
    let cards = '';
    CASE_TYPES.forEach(function(t) {
        cards += '<button class="quiz-type-card" onclick="showCase(\'' + t.id + '\')" style="border-color:#f59e0b">' +
            '<span class="quiz-type-icon">' + t.icon + '</span>' +
            '<span class="quiz-type-name">' + t.name + '</span>' +
            '<span class="quiz-type-desc">' + t.desc + '</span></button>';
    });
    div.innerHTML = getBotAvatar() +
        '<div class="bubble"><b>📰 真实案例分享</b><br>选择诈骗类型,查看国内近期发生的真实案例,从别人的教训中学习防骗知识!<br><br>' +
        '<div class="quiz-type-grid">' + cards + '</div>' +
        '<span style="font-size:12px;opacity:0.6">案例来自新闻报道和警方通报,一次展示一个~</span></div>';
    chatArea.appendChild(div);
    scrollToBottom();
}

async function showCase(category) {
    caseActive = true;

    // 加载中提示
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot';
    loadingDiv.id = 'caseLoading';
    loadingDiv.innerHTML = getBotAvatar() +
        '<div class="bubble case-loading">小哨正在翻阅案例库 <span class="dots"><span></span><span></span><span></span></span></div>';
    chatArea.appendChild(loadingDiv);
    scrollToBottom();

    try {
        const seen = caseSeenTitles[category] || [];
        const params = new URLSearchParams({ category: category });
        seen.forEach(function(t) { params.append('exclude', t); });
        const res = await fetch('/api/fraud-cases?' + params.toString());
        const data = await res.json();

        const loadingEl = document.getElementById('caseLoading');
        if (loadingEl) loadingEl.remove();

        if (data.error || !data.cases || data.cases.length === 0) {
            addBotMessage('⚠️ 暂时没有找到该类型的案例,请稍后再试~');
            caseActive = false;
            return;
        }

        renderCaseCard(data.cases[0], category);
    } catch (err) {
        const loadingEl = document.getElementById('caseLoading');
        if (loadingEl) loadingEl.remove();
        addBotMessage('⚠️ 案例加载失败,请检查网络后重试~');
        caseActive = false;
    }
}

function renderCaseCard(c, category) {
    // 记录已看标题
    if (!caseSeenTitles[category]) caseSeenTitles[category] = [];
    caseSeenTitles[category].push(c.title);

    // 找分类信息
    const typeInfo = CASE_TYPES.find(function(t) { return t.id === category; });
    const typeName = typeInfo ? typeInfo.name : category;

    const div = document.createElement('div');
    div.className = 'message bot';

    // 法院判决要点(如果有)
    let rulingHtml = '';
    if (c.court_ruling) {
        rulingHtml = '<div style="margin:8px 0;padding:8px 12px;border-radius:8px;background:rgba(99,102,241,0.08);border-left:3px solid #6366f1">' +
            '<div style="font-size:12px;font-weight:600;color:#6366f1;margin-bottom:4px">⚖️ 法院判决要点</div>' +
            '<div style="font-size:12px;opacity:0.85">' + escapeHtml(c.court_ruling) + '</div></div>';
    }

    // 人民法院案例库链接(如果有)
    let courtLinkHtml = '';
    if (c.court_db_url) {
        courtLinkHtml = '<div style="margin:8px 0;padding:6px 12px;border-radius:8px;background:rgba(37,99,235,0.06);font-size:12px">' +
            '📋 案例来源:<a href="' + c.court_db_url + '" target="_blank" style="color:#2563eb;text-decoration:underline">人民法院案例库</a>' +
            ' <span style="opacity:0.6">(点击查看更多真实判例)</span></div>';
    }

    div.innerHTML = getBotAvatar() +
        '<div class="bubble" style="padding:0;overflow:hidden">' +
        '<div class="case-card" style="margin:0;border-radius:0;border-left:none;border-top:4px solid #f59e0b">' +
        '<div class="case-card-header">' +
        '<span class="case-card-title">' + escapeHtml(c.title) + '</span>' +
        '<span class="case-card-source">' + escapeHtml(c.source || '网络') + '</span>' +
        (c.date ? '<span class="case-card-date">' + escapeHtml(c.date) + '</span>' : '') +
        '</div>' +
        '<div class="case-card-content">' + escapeHtml(c.content) + '</div>' +
        rulingHtml +
        '<div class="case-card-lesson"><span class="lesson-icon">⚠️</span><span>' + escapeHtml(c.lesson) + '</span></div>' +
        courtLinkHtml +
        '<div class="case-card-actions">' +
        '<button class="case-action-btn primary" onclick="showCase(\'' + category + '\')">📖 再来一个</button>' +
        '<button class="case-action-btn secondary" onclick="quitCase()">返回</button>' +
        '</div>' +
        '<div class="case-count-hint">当前分类: ' + typeName + ' | 已看 ' + (caseSeenTitles[category].length) + ' 个案例</div>' +
        '</div></div>';
    chatArea.appendChild(div);
    scrollToBottom();
}

function quitCase(silent) {
    caseActive = false;
    if (activeModule === 'case') activeModule = null;
    if (!silent) addBotMessage('👋 已退出案例分享。想学习更多案例随时点「📰 真实案例」!');
}

// ===== 反诈雷达 =====
let radarActive = false;

async function startRadar() {
    if (radarActive) return;
    switchModule('radar');
    radarActive = true;

    const div = document.createElement('div');
    div.className = 'message bot';
    div.innerHTML = getBotAvatar() +
        '<div class="bubble">' +
        '<b>🔍 反诈雷达</b><br>' +
        '输入手机号、网址或APP名称,小哨立刻帮你查询是否为已知高风险诈骗源!<br><br>' +
        '<div class="radar-search-box">' +
        '<input type="text" id="radarInput" placeholder="输入手机号/网址/APP名称..." onkeydown="if(event.key===\'Enter\')doRadarCheck()">' +
        '<button class="radar-search-btn" onclick="doRadarCheck()">查询</button>' +
        '</div>' +
        '<div id="radarResult"></div>' +
        '<div style="margin-top:12px;border-top:1px solid var(--border-color);padding-top:10px">' +
        '<b>📢 本周高发诈骗预警</b><div id="radarAlerts" style="margin-top:8px"></div>' +
        '</div>' +
        '<div class="case-card-actions" style="margin-top:10px">' +
        '<button class="case-action-btn secondary" onclick="quitRadar()">返回</button>' +
        '</div>' +
        '</div>';
    chatArea.appendChild(div);
    scrollToBottom();

    // 加载预警信息
    try {
        const res = await fetch('/api/scam-alerts');
        const data = await res.json();
        const alertsDiv = document.getElementById('radarAlerts');
        if (alertsDiv && data.alerts) {
            let html = '';
            data.alerts.forEach(function(a) {
                html += '<div class="alert-card">' +
                    '<div class="alert-card-header">' +
                    '<span class="alert-card-title">' + a.title + '</span>' +
                    '<span class="alert-card-level" style="background:rgba(239,68,68,0.15);color:#dc2626">' + a.level + '</span>' +
                    '</div>' +
                    '<div class="alert-card-desc">' + a.desc + '</div>' +
                    '<div class="alert-card-tip">💡 ' + a.tip + '</div>' +
                    '</div>';
            });
            alertsDiv.innerHTML = html;
        }
    } catch (e) {}

    const input = document.getElementById('radarInput');
    if (input) input.focus();
}

async function doRadarCheck() {
    const input = document.getElementById('radarInput');
    const resultDiv = document.getElementById('radarResult');
    if (!input || !resultDiv) return;

    const query = input.value.trim();
    if (!query) {
        resultDiv.innerHTML = '<span style="font-size:12px;color:#ef4444">请输入要查询的内容</span>';
        return;
    }

    resultDiv.innerHTML = '<span style="font-size:12px;opacity:0.6">🔍 正在查询...</span>';

    try {
        const res = await fetch('/api/fraud-check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const data = await res.json();

        if (data.error) {
            resultDiv.innerHTML = '<span style="font-size:12px;color:#ef4444">' + data.error + '</span>';
            return;
        }

        const riskClass = data.risk || 'unknown';
        const riskLabel = { high: '🔴 高风险', medium: '🟠 中风险', low: '🟢 低风险', unknown: '⚪ 未知' }[riskClass] || '⚪ 未知';
        const typeLabel = { phone: '手机号', url: '网址', app: 'APP' }[data.type] || '未知类型';

        resultDiv.innerHTML =
            '<div class="radar-result ' + riskClass + '">' +
            '<div class="radar-result-header">' +
            '<span class="radar-risk-badge ' + riskClass + '">' + riskLabel + '</span>' +
            '<span style="font-size:12px;opacity:0.6">类型: ' + typeLabel + '</span>' +
            '</div>' +
            '<div class="radar-result-reason">' + data.reason + '</div>' +
            '<div class="radar-result-advice">💡 ' + data.advice + '</div>' +
            '</div>';
    } catch (e) {
        resultDiv.innerHTML = '<span style="font-size:12px;color:#ef4444">查询失败,请检查网络</span>';
    }

    input.value = '';
    scrollToBottom();
}

function quitRadar(silent) {
    radarActive = false;
    if (activeModule === 'radar') activeModule = null;
    if (!silent) addBotMessage('👋 已退出反诈雷达。随时点「🔍 反诈雷达」查询可疑号码/网址/APP!');
}

// ===== 模拟演练 =====
let roleplayActive = false;
let roleplaySessionKey = 'roleplay-' + Date.now();
let roleplayEndBar = null; // 结束按钮容器(始终跟随最新消息)

function startRoleplaySelect() {
    if (roleplayActive) return;
    switchModule('roleplay');
    const div = document.createElement('div');
    div.className = 'message bot';
    div.innerHTML = getBotAvatar() +
        '<div class="bubble"><b>🎭 模拟演练</b><br>' +
        '按<b>6大诈骗套路</b>选择分类,小哨将扮演骗子与你实时对话!<br>' +
        '在安全环境中体验真实诈骗话术,训练你的防骗反应。<br>' +
        '<span style="font-size:12px;opacity:0.6">💡 每次演练随机生成不同骗子形象,结束后给出复盘点评~</span><br><br>' +
        '<div id="roleplayCategories">加载中...</div></div>';
    chatArea.appendChild(div);
    scrollToBottom();

    // 加载分类角色列表
    fetch('/api/roleplay-categories')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            roleplayCategoryData = data; // 缓存数据
            const container = document.getElementById('roleplayCategories');
            if (!container) return;
            // 复用 QUIZ_CATEGORIES 的分类名称和图标
            const catInfo = {};
            if (typeof QUIZ_CATEGORIES !== 'undefined') {
                QUIZ_CATEGORIES.forEach(function(c) { catInfo[c.id] = c; });
            }
            let html = '<div class="quiz-type-grid">';
            data.categories.forEach(function(cat) {
                const info = catInfo[cat.id] || { icon: '🎭', name: cat.id, desc: '', slogan: '' };
                html += '<button class="quiz-type-card" onclick="showRoleplayCategoryScenes(\'' + cat.id + '\')" style="border-color:#8b5cf6">' +
                    '<span class="quiz-type-icon">' + info.icon + '</span>' +
                    '<span class="quiz-type-name">' + info.name + '</span>' +
                    '<span class="quiz-type-desc">' + info.desc + ' · ' + cat.personas.length + '个角色</span></button>';
            });
            html += '</div>';
            container.innerHTML = html;
        })
        .catch(function() {
            const container = document.getElementById('roleplayCategories');
            if (container) container.innerHTML = '<span style="font-size:12px;color:#ef4444">加载失败,请重试</span>';
        });
}

// 缓存分类数据
let roleplayCategoryData = null;

function showRoleplayCategoryScenes(catId) {
    // 先加载分类数据(如果还没加载)
    if (!roleplayCategoryData) {
        fetch('/api/roleplay-categories')
            .then(function(r) { return r.json(); })
            .then(function(data) { roleplayCategoryData = data; renderRoleplayCategoryScenes(catId); })
            .catch(function() { addBotMessage('⚠️ 加载失败,请重试'); });
        return;
    }
    renderRoleplayCategoryScenes(catId);
}

function renderRoleplayCategoryScenes(catId) {
    const cat = roleplayCategoryData.categories.find(function(c) { return c.id === catId; });
    if (!cat) return;

    // 获取分类信息
    const catInfo = {};
    if (typeof QUIZ_CATEGORIES !== 'undefined') {
        QUIZ_CATEGORIES.forEach(function(c) { catInfo[c.id] = c; });
    }
    const info = catInfo[catId] || { icon: '🎭', name: catId, slogan: '' };

    const div = document.createElement('div');
    div.className = 'message bot';
    let cards = '';
    cat.personas.forEach(function(p) {
        cards += '<button class="quiz-type-card" onclick="startRoleplay(\'' + p.id + '\')" style="border-color:#8b5cf6">' +
            '<span class="quiz-type-icon">' + p.icon + '</span>' +
            '<span class="quiz-type-name">' + p.name + '</span>' +
            '<span class="quiz-type-desc">' + p.difficulty + ' ' + p.desc + '</span></button>';
    });
    // 随机来一个按钮
    const randomIds = cat.personas.map(function(p) { return p.id; });
    cards += '<button class="quiz-type-card" onclick="startRoleplay(\'' + randomIds[Math.floor(Math.random() * randomIds.length)] + '\')" style="border-color:var(--input-focus)">' +
        '<span class="quiz-type-icon">🎲</span>' +
        '<span class="quiz-type-name">随机来一个</span>' +
        '<span class="quiz-type-desc">随机选一个骗子开练</span></button>';
    div.innerHTML = getBotAvatar() +
        '<div class="bubble"><b>' + info.icon + ' ' + info.name + ' · 模拟演练</b><br>' +
        '<span style="font-size:12px;opacity:0.7">' + (info.slogan || info.desc || '') + '</span><br><br>' +
        '<div class="quiz-type-grid">' + cards + '</div>' +
        '<span style="font-size:12px;opacity:0.6">选择一个骗子角色开始演练,或点「🎲 随机来一个」!</span></div>';
    chatArea.appendChild(div);
    scrollToBottom();
}

async function startRoleplay(personaId) {
    roleplayActive = true;
    roleplaySessionKey = 'roleplay-' + Date.now() + '-' + Math.random().toString(36).substr(2, 6);

    // 立即显示演练头部+退出按钮(不等API)
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message bot';
    headerDiv.innerHTML = getBotAvatar() +
        '<div class="bubble">' +
        '<div class="roleplay-header">🎭 模拟演练中' +
        ' <span style="font-size:11px;opacity:0.6;margin-left:auto">直接在下方输入框回复骗子</span></div>' +
        '<span style="font-size:11px;opacity:0.5">💡 像真实情况一样回应。识破了就明确拒绝,想结束点「结束演练」</span>' +
        '</div>';
    chatArea.appendChild(headerDiv);

    // 立即创建结束按钮容器
    createRoleplayEndBar();

    // 显示"正在连接"占位
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot';
    loadingDiv.id = 'roleplayLoading';
    loadingDiv.innerHTML = getBotAvatar() +
        '<div class="bubble case-loading">骗子正在拨号... <span class="dots"><span></span><span></span><span></span></span></div>';
    moveRoleplayEndBarAfter(loadingDiv);
    chatArea.appendChild(loadingDiv);
    moveRoleplayEndBarAfter(loadingDiv);
    scrollToBottom();

    try {
        const res = await fetch('/api/roleplay-start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ persona_id: personaId, session_key: roleplaySessionKey })
        });
        const data = await res.json();

        const loadingEl = document.getElementById('roleplayLoading');
        if (loadingEl) loadingEl.remove();

        if (data.error) {
            addBotMessage('⚠️ ' + data.error);
            roleplayActive = false;
            removeRoleplayEndBar();
            return;
        }

        // 更新头部信息
        const header = headerDiv.querySelector('.roleplay-header');
        if (header) header.innerHTML = data.persona_icon + ' 模拟演练中: ' + data.persona_name +
            ' <span style="font-size:11px;opacity:0.6;margin-left:auto">直接在下方输入框回复骗子</span>';

        // 显示骗子开场白
        addRoleplayScammerMsg(data.opening);
    } catch (e) {
        const loadingEl = document.getElementById('roleplayLoading');
        if (loadingEl) loadingEl.remove();
        addBotMessage('⚠️ 演练启动失败,请检查网络');
        roleplayActive = false;
        removeRoleplayEndBar();
    }
}

// 创建结束按钮容器(始终在最新消息下方)
function createRoleplayEndBar() {
    removeRoleplayEndBar();
    roleplayEndBar = document.createElement('div');
    roleplayEndBar.id = 'roleplayEndBar';
    roleplayEndBar.innerHTML = '<div class="roleplay-actions" style="padding:6px 20px">' +
        '<button class="roleplay-action-btn end-btn" onclick="endRoleplay()">🏁 结束演练并复盘</button>' +
        '</div>';
    chatArea.appendChild(roleplayEndBar);
}

// 将结束按钮移到指定元素之后
function moveRoleplayEndBarAfter(el) {
    if (!roleplayEndBar || !el) return;
    if (el.nextSibling) {
        chatArea.insertBefore(roleplayEndBar, el.nextSibling);
    } else {
        chatArea.appendChild(roleplayEndBar);
    }
}

function removeRoleplayEndBar() {
    if (roleplayEndBar) {
        roleplayEndBar.remove();
        roleplayEndBar = null;
    }
    const old = document.getElementById('roleplayEndBar');
    if (old) old.remove();
}

function addRoleplayScammerMsg(text) {
    const div = document.createElement('div');
    div.className = 'message bot';
    const formatted = escapeHtml(text).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
    div.innerHTML = getBotAvatar() + '<div class="bubble roleplay-msg-scammer">' + formatted + '</div>';
    chatArea.appendChild(div);
    // 结束按钮跟随到最新消息下方
    moveRoleplayEndBarAfter(div);
    scrollToBottom();
}

async function sendRoleplayMessage(text) {
    if (!roleplayActive || !text.trim()) return;

    // 显示用户消息
    addUserMessage(text);

    // 加载中
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot';
    loadingDiv.id = 'roleplayThinking';
    loadingDiv.innerHTML = getBotAvatar() + '<div class="bubble case-loading">骗子正在输入... <span class="dots"><span></span><span></span><span></span></span></div>';
    chatArea.appendChild(loadingDiv);
    moveRoleplayEndBarAfter(loadingDiv);
    scrollToBottom();

    try {
        const res = await fetch('/api/roleplay-chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_key: roleplaySessionKey, message: text })
        });
        const data = await res.json();

        const thinkingEl = document.getElementById('roleplayThinking');
        if (thinkingEl) thinkingEl.remove();

        if (data.error) {
            addBotMessage('⚠️ ' + data.error);
            return;
        }

        addRoleplayScammerMsg(data.reply);

        if (data.ended) {
            setTimeout(function() { endRoleplay(); }, 1500);
        }
    } catch (e) {
        const thinkingEl = document.getElementById('roleplayThinking');
        if (thinkingEl) thinkingEl.remove();
        addBotMessage('⚠️ 演练对话失败,请检查网络');
    }
}

async function endRoleplay(silent) {
    if (!roleplayActive) return;
    roleplayActive = false;
    if (activeModule === 'roleplay') activeModule = null;

    removeRoleplayEndBar();

    // 静默退出(模块切换),不生成复盘
    if (silent) return;

    // 获取复盘
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot';
    loadingDiv.id = 'roleplayEvalLoading';
    loadingDiv.innerHTML = getBotAvatar() + '<div class="bubble case-loading">正在生成复盘... <span class="dots"><span></span><span></span><span></span></span></div>';
    chatArea.appendChild(loadingDiv);
    scrollToBottom();

    try {
        const res = await fetch('/api/roleplay-end', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_key: roleplaySessionKey })
        });
        const data = await res.json();

        const loadingEl = document.getElementById('roleplayEvalLoading');
        if (loadingEl) loadingEl.remove();

        if (data.error) {
            addBotMessage('⚠️ ' + data.error);
            return;
        }

        addBotMessage(data.evaluation);
    } catch (e) {
        const loadingEl = document.getElementById('roleplayEvalLoading');
        if (loadingEl) loadingEl.remove();
        addBotMessage('⚠️ 复盘生成失败');
    }
}

// ===== 证据分析 =====
let evidenceActive = false;

function startEvidenceSelect() {
    if (evidenceActive) return;
    switchModule('evidence');
    evidenceActive = true;

    const div = document.createElement('div');
    div.className = 'message bot';
    div.innerHTML = getBotAvatar() +
        '<div class="bubble"><b>📎 证据分析</b><br>' +
        '描述你遇到的情况或粘贴和骗子的聊天记录,小哨自动帮你:<br>' +
        '<span style="font-size:12px">🔍 检测诈骗话术 → 🏷️ 识别诈骗类型 → 📝 生成报案草稿 → ❓ 追问缺失细节</span><br><br>' +
        '<textarea class="evidence-textarea" id="evidenceInput" placeholder="描述你遇到的情况,或粘贴聊天记录...&#10;例如:我接到自称快递客服的电话,说包裹丢了可以理赔,让我加QQ..."></textarea>' +
        '<button class="evidence-submit-btn" onclick="doEvidenceAnalyze()">🔍 开始分析</button>' +
        '<div id="evidenceResult" style="margin-top:10px"></div>' +
        '<div class="case-card-actions" style="margin-top:10px">' +
        '<button class="case-action-btn secondary" onclick="quitEvidence()">返回</button>' +
        '</div>' +
        '</div>';
    chatArea.appendChild(div);
    scrollToBottom();
}

let evidenceSessionKey = 'evidence-' + Date.now();

async function doEvidenceAnalyze() {
    const input = document.getElementById('evidenceInput');
    const resultDiv = document.getElementById('evidenceResult');
    if (!input || !resultDiv) return;

    const text = input.value.trim();
    if (!text) {
        resultDiv.innerHTML = '<span style="font-size:12px;color:#ef4444">请先描述你遇到的情况</span>';
        return;
    }

    evidenceSessionKey = 'evidence-' + Date.now() + '-' + Math.random().toString(36).substr(2, 6);
    resultDiv.innerHTML = '<span style="font-size:12px;opacity:0.6">🔍 正在分析...</span>';

    try {
        const res = await fetch('/api/evidence-analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, session_key: evidenceSessionKey })
        });
        const data = await res.json();

        if (data.error) {
            resultDiv.innerHTML = '<span style="font-size:12px;color:#ef4444">' + data.error + '</span>';
            return;
        }

        renderEvidenceResult(data, resultDiv);
    } catch (e) {
        resultDiv.innerHTML = '<span style="font-size:12px;color:#ef4444">分析失败,请检查网络</span>';
    }
    scrollToBottom();
}

function renderEvidenceResult(data, container) {
    const analysis = data.analysis;
    let html = '';

    // 检测结果
    html += '<div class="evidence-summary ' + analysis.risk_level + '">' + analysis.summary + '</div>';

    // 诈骗类型
    if (analysis.scam_types && analysis.scam_types.length > 0) {
        html += '<div style="font-size:13px;font-weight:600;margin:8px 0">🏷️ 识别的诈骗类型: ' +
            analysis.scam_types.map(function(t) { return '<span style="padding:2px 8px;border-radius:8px;background:rgba(239,68,68,0.1);color:#dc2626;margin:2px">' + escapeHtml(t) + '</span>'; }).join('') +
            '</div>';
    }

    // 话术详情
    if (analysis.found_patterns && analysis.found_patterns.length > 0) {
        analysis.found_patterns.forEach(function(p) {
            const levelClass = p.level.includes('极高危') ? 'extreme' : (p.level.includes('高危') ? 'high' : 'medium');
            html += '<div class="evidence-pattern-item ' + levelClass + '">' +
                '<div class="evidence-pattern-label">' + escapeHtml(p.level || '') + ' ' + escapeHtml(p.label) + '</div>' +
                (p.matched_text ? '<div class="evidence-pattern-text">「' + escapeHtml(p.matched_text) + '」</div>' : '') +
                '<div class="evidence-pattern-analysis">' + escapeHtml(p.analysis) + '</div>' +
                '</div>';
        });
    }

    // 关键发现
    if (analysis.key_findings && analysis.key_findings.length > 0) {
        html += '<div style="margin-top:10px;font-size:13px;font-weight:600">🔍 关键发现:</div>';
        analysis.key_findings.forEach(function(f) {
            html += '<div style="font-size:12px;opacity:0.85;margin:4px 0;padding:4px 10px;border-radius:6px;background:rgba(239,68,68,0.06)">• ' + escapeHtml(f) + '</div>';
        });
    }

    // 核心建议
    if (analysis.advice) {
        html += '<div style="margin-top:10px;font-size:13px;font-weight:600;color:#16a34a">💡 小哨建议:</div>';
        html += '<div style="font-size:12px;opacity:0.9;margin:4px 0;padding:6px 10px;border-radius:6px;background:rgba(22,163,74,0.08)">' + escapeHtml(analysis.advice) + '</div>';
    }

    // 小哨讲解视频(放在建议下方)
    html += '<div id="evidenceVideoSlot" style="margin-top:10px"></div>';

    // 报案草稿
    html += '<div style="margin-top:12px;font-size:13px;font-weight:600">📝 报案草稿(自动生成)</div>';
    html += '<div class="report-draft-box" id="reportDraftBox">' + escapeHtml(data.draft) + '</div>';
    html += '<button class="report-copy-btn" onclick="copyReportDraft()">📋 复制草稿</button>';

    // 追问问题(每次1-3个)
    html += renderFollowupQuestions(data.followup_questions, data.has_questions);

    container.innerHTML = html;
    scrollToBottom();

    // 异步加载视频
    loadMascotVideo('evidenceVideoSlot');
}

// 渲染追问问题区域(每次1-3个)
function renderFollowupQuestions(questions, hasQuestions) {
    let html = '';
    if (hasQuestions && questions && questions.length > 0) {
        html += '<div data-question-section style="margin-top:12px;font-size:13px;font-weight:600;color:#6366f1">❓ 小哨还需要了解以下细节来完善草稿:</div>';
        questions.forEach(function(q, i) {
            html += '<div data-question-section style="margin-top:8px">' +
                '<div style="font-size:12px;opacity:0.8;margin-bottom:4px">' + (i + 1) + '. ' + escapeHtml(q.question) + '</div>' +
                '<input type="text" class="evidence-answer-input" data-qid="' + q.id + '" placeholder="输入你的回答..." style="width:100%;padding:8px 12px;border:1.5px solid #6366f1;border-radius:8px;font-size:13px;background:var(--input-bg);color:var(--text-color);outline:none;box-sizing:border-box">' +
                '</div>';
        });
        html += '<button data-question-section class="evidence-submit-btn" style="background:#6366f1;margin-top:10px" onclick="submitEvidenceAnswers()">✅ 补充信息并更新草稿</button>';
    } else {
        html += '<div data-question-section style="margin-top:8px;font-size:12px;color:#16a34a">✅ 草稿信息已完整!请补充个人信息后带到派出所报案。</div>';
    }
    return html;
}

async function submitEvidenceAnswers() {
    const inputs = document.querySelectorAll('.evidence-answer-input:not([disabled])');
    const answers = {};
    inputs.forEach(function(inp) {
        const val = inp.value.trim();
        if (val) answers[inp.dataset.qid] = val;
    });

    if (Object.keys(answers).length === 0) {
        showToast('请至少填写一个回答');
        return;
    }

    // 禁用当前输入框和按钮,防止重复提交
    inputs.forEach(function(inp) { inp.disabled = true; });
    const submitBtns = document.querySelectorAll('[data-question-section].evidence-submit-btn');
    submitBtns.forEach(function(b) { b.disabled = true; b.textContent = '📝 更新中...'; });

    try {
        const res = await fetch('/api/evidence-answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_key: evidenceSessionKey, answers: answers })
        });
        const data = await res.json();

        if (data.error) {
            inputs.forEach(function(inp) { inp.disabled = false; });
            submitBtns.forEach(function(b) { b.disabled = false; b.textContent = '✅ 补充信息并更新草稿'; });
            showToast(data.error);
            return;
        }

        // 更新草稿显示
        const draftBox = document.getElementById('reportDraftBox');
        if (draftBox) draftBox.textContent = data.draft;

        // 移除旧的追问区域
        const resultDiv = document.getElementById('evidenceResult');
        if (resultDiv) {
            resultDiv.querySelectorAll('[data-question-section]').forEach(function(el) { el.remove(); });
        }

        // 在复制按钮后插入新的追问区域(下一批1-3个问题)
        const copyBtn = document.querySelector('.report-copy-btn');
        if (copyBtn) {
            copyBtn.insertAdjacentHTML('afterend', renderFollowupQuestions(data.remaining_questions, data.has_questions));
        }

        // 在草稿框下方插入新视频槽位(补充后的视频)
        if (draftBox) {
            const videoSlotId = 'evidenceVideoUpdate-' + Date.now();
            const videoSlot = document.createElement('div');
            videoSlot.id = videoSlotId;
            videoSlot.style.marginTop = '10px';
            draftBox.insertAdjacentElement('afterend', videoSlot);
            loadMascotVideo(videoSlotId);
        }

        showToast('草稿已更新!');
    } catch (e) {
        inputs.forEach(function(inp) { inp.disabled = false; });
        submitBtns.forEach(function(b) { b.disabled = false; b.textContent = '✅ 补充信息并更新草稿'; });
        showToast('更新失败,请检查网络');
    }
    scrollToBottom();
}

function copyReportDraft() {
    const box = document.getElementById('reportDraftBox');
    if (!box) return;
    const text = box.textContent;
    navigator.clipboard.writeText(text).then(function() {
        showToast('草稿已复制到剪贴板!');
    }).catch(function() {
        showToast('复制失败,请手动选择复制');
    });
}

// ===== 小哨讲解视频(自定义播放器+TTS配音) =====
let videoInstanceId = 0;

async function loadMascotVideo(slotId) {
    const slot = document.getElementById(slotId);
    if (!slot) return;

    slot.innerHTML = '<div class="case-loading">🐧 小哨正在准备讲解... <span class="dots"><span></span><span></span><span></span></span></div>';
    scrollToBottom();

    try {
        const res = await fetch('/api/evidence-video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_key: evidenceSessionKey })
        });
        const data = await res.json();

        if (data.error || !data.slides || data.slides.length === 0) {
            slot.innerHTML = '';
            return;
        }

        renderPptPlayer(data.slides, slot);
    } catch (e) {
        slot.innerHTML = '';
    }
}

// ===== PPT幻灯片播放器(切换时自动播放柔和语音) =====
function renderPptPlayer(slides, container) {
    videoInstanceId++;
    const vid = 'xppt-' + videoInstanceId;

    const div = document.createElement('div');
    div.className = 'xppt-player';
    div.id = vid;

    // 构建幻灯片HTML
    let slidesHtml = '';
    slides.forEach(function(s, i) {
        slidesHtml += '<div class="xppt-slide' + (i === 0 ? ' active' : '') + '" data-slide="' + i + '">' +
            '<div class="xppt-slide-icon">' + escapeHtml(s.icon || '🐧') + '</div>' +
            (s.title ? '<div class="xppt-slide-title">' + escapeHtml(s.title) + '</div>' : '') +
            '<div class="xppt-slide-text">' + escapeHtml(s.text) + '</div>' +
            '</div>';
    });

    // 导航圆点
    let dotsHtml = '';
    slides.forEach(function(_, i) {
        dotsHtml += '<button class="xppt-dot' + (i === 0 ? ' active' : '') + '" data-idx="' + i + '"></button>';
    });

    div.innerHTML =
        '<div class="xppt-header">' +
            '<span class="xppt-title">🐧 小哨为你讲解</span>' +
            '<button class="xppt-sound-btn" title="静音/取消静音">🔊</button>' +
        '</div>' +
        '<div class="xppt-stage">' +
            '<div class="xppt-mascot-wrap">' + MASCOT_SVG + '</div>' +
            '<div class="xppt-content">' + slidesHtml + '</div>' +
        '</div>' +
        '<div class="xppt-nav">' +
            '<button class="xppt-arrow xppt-prev" title="上一页">‹</button>' +
            '<div class="xppt-dots">' + dotsHtml + '</div>' +
            '<button class="xppt-arrow xppt-next" title="下一页">›</button>' +
        '</div>';

    container.innerHTML = '';
    container.appendChild(div);
    scrollToBottom();

    // ===== PPT逻辑 =====
    let current = 0;
    let muted = false;
    const total = slides.length;
    const slideEls = div.querySelectorAll('.xppt-slide');
    const dotEls = div.querySelectorAll('.xppt-dot');
    const prevBtn = div.querySelector('.xppt-prev');
    const nextBtn = div.querySelector('.xppt-next');
    const soundBtn = div.querySelector('.xppt-sound-btn');

    // 柔和语音播放
    function speakSlide(idx) {
        if (muted) return;
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        const s = slides[idx];
        const text = (s.title ? s.title + '。' : '') + s.text;
        const u = new SpeechSynthesisUtterance(text);
        u.lang = 'zh-CN';
        u.rate = 0.9;   // 稍慢,更柔和
        u.pitch = 1.15; // 稍高但不尖锐
        u.volume = 0.9;
        // 优先选柔和的中文女声
        const voices = window.speechSynthesis.getVoices();
        const zhVoice = voices.find(function(v) { return v.lang.startsWith('zh') && /Xiaoxiao|Yaoyao|Huihui|Tingting|female|女/i.test(v.name); })
            || voices.find(function(v) { return v.lang.startsWith('zh'); });
        if (zhVoice) u.voice = zhVoice;
        window.speechSynthesis.speak(u);
    }

    function showSlide(idx) {
        if (idx < 0) idx = 0;
        if (idx >= total) idx = total - 1;
        current = idx;
        slideEls.forEach(function(s, i) {
            s.classList.toggle('active', i === idx);
            if (i === idx) {
                s.style.animation = 'none';
                void s.offsetWidth;
                s.style.animation = 'slideFadeIn 0.4s ease';
            }
        });
        dotEls.forEach(function(d, i) {
            d.classList.toggle('active', i === idx);
        });
        // 切换PPT时播放对应语音
        speakSlide(idx);
    }

    prevBtn.addEventListener('click', function() { showSlide(current - 1); });
    nextBtn.addEventListener('click', function() { showSlide(current + 1); });
    dotEls.forEach(function(d) {
        d.addEventListener('click', function() { showSlide(parseInt(d.dataset.idx)); });
    });

    // 静音切换
    soundBtn.addEventListener('click', function() {
        muted = !muted;
        soundBtn.textContent = muted ? '🔇' : '🔊';
        if (muted && 'speechSynthesis' in window) window.speechSynthesis.cancel();
    });

    // 首次显示第一页并播放语音
    showSlide(0);

    // 页面卸载时停止TTS
    window.addEventListener('beforeunload', function() {
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    });
}

function quitEvidence(silent) {
    evidenceActive = false;
    if (activeModule === 'evidence') activeModule = null;
    if (!silent) addBotMessage('👋 已退出证据分析。需要分析聊天记录或生成报案草稿时,随时点「📎 证据分析」!');
}


// ===== 初始化 =====
initMascots();
initTheme();
refreshUserAvatars();
applyBackground();
userInput.focus();