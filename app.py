<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>台南市停車場查詢</title>

  <!-- PWA -->
  <link rel="manifest" href="./manifest.json" />
  <meta name="theme-color" content="#0f5a3c" />
  <meta name="mobile-web-app-capable" content="yes" />

  <!-- iOS PWA -->
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <meta name="apple-mobile-web-app-title" content="台南停車場" />
  <link rel="apple-touch-icon" href="./icons/apple-touch-icon.png" />

  <!-- Favicons -->
  <link rel="icon" type="image/png" sizes="32x32" href="./icons/favicon-32x32.png" />
  <link rel="icon" type="image/png" sizes="16x16" href="./icons/favicon-16x16.png" />

  <!-- SEO / OG -->
  <meta name="description" content="查詢台南市各行政區停車場即時資訊" />
  <meta property="og:title" content="台南市停車場查詢系統" />
  <meta property="og:description" content="查詢台南市各行政區停車場即時資訊，資料來源：台南市政府開放資料平台" />
  <meta property="og:image" content="./icons/icon-512x512.png" />
  <meta property="og:type" content="website" />

  <style>
    /* ── Reset & Base ─────────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --green-900: #0a3223;
      --green-700: #0f5a3c;
      --green-500: #1a7a52;
      --gold:      #ffc800;
      --gold-dim:  #c89e00;
      --white:     #f0f6f2;
      --text-dim:  #8ab09a;
      --header-h:  56px;
      --footer-h:  42px;
      --radius:    14px;
      --shadow:    0 4px 24px rgba(0,0,0,.45);
      --font-ui:   'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
    }

    html, body {
      height: 100%;
      overflow: hidden;
      background: var(--green-900);
      color: var(--white);
      font-family: var(--font-ui);
      -webkit-font-smoothing: antialiased;
    }

    /* ── Layout ───────────────────────────────────────── */
    #app {
      display: flex;
      flex-direction: column;
      height: 100%;
      height: 100dvh;          /* dynamic viewport height for mobile browsers */
    }

    /* ── Header ───────────────────────────────────────── */
    header {
      flex: 0 0 var(--header-h);
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 0 16px;
      background: linear-gradient(135deg, var(--green-700), var(--green-900));
      box-shadow: 0 2px 12px rgba(0,0,0,.4);
      position: relative;
      z-index: 10;
      /* safe-area for iPhone notch */
      padding-top: env(safe-area-inset-top);
    }

    .header-icon {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      flex-shrink: 0;
    }

    .header-title {
      font-size: 1rem;
      font-weight: 700;
      color: var(--white);
      letter-spacing: .04em;
      line-height: 1.2;
    }

    .header-sub {
      font-size: .65rem;
      color: var(--text-dim);
      letter-spacing: .02em;
    }

    .header-spacer { flex: 1; }

    /* 網路狀態燈 */
    #net-badge {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: .65rem;
      color: var(--text-dim);
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.1);
      border-radius: 20px;
      padding: 4px 10px;
      transition: all .3s;
    }
    #net-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--gold);
      transition: background .4s;
    }
    #net-badge.online  #net-dot { background: #4cdf84; }
    #net-badge.offline #net-dot { background: #f05a5a; }
    #net-badge.online  #net-label::after  { content: '線上'; }
    #net-badge.offline #net-label::after { content: '離線'; }

    /* ── Main iframe area ─────────────────────────────── */
    main {
      flex: 1 1 0;
      position: relative;
      overflow: hidden;
    }

    #parking-frame {
      width: 100%;
      height: 100%;
      border: none;
      display: block;
      background: var(--green-900);
      transition: opacity .4s;
    }

    /* ── Splash / Loading overlay ─────────────────────── */
    #splash {
      position: absolute;
      inset: 0;
      background: var(--green-900);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 20px;
      z-index: 20;
      transition: opacity .5s, visibility .5s;
    }
    #splash.hidden {
      opacity: 0;
      visibility: hidden;
      pointer-events: none;
    }

    .splash-logo {
      width: 96px;
      height: 96px;
      border-radius: 22px;
      box-shadow: var(--shadow);
      animation: pop .6s cubic-bezier(.34,1.56,.64,1) both;
    }
    @keyframes pop {
      from { transform: scale(.5); opacity: 0; }
      to   { transform: scale(1);  opacity: 1; }
    }

    .splash-text {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--white);
      letter-spacing: .06em;
      animation: fadein .6s .2s both;
    }
    @keyframes fadein {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0);   }
    }

    /* Spinner */
    .spinner {
      width: 36px;
      height: 36px;
      border: 3px solid rgba(255,200,0,.2);
      border-top-color: var(--gold);
      border-radius: 50%;
      animation: spin 1s linear infinite, fadein .6s .4s both;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── Offline Banner ───────────────────────────────── */
    #offline-banner {
      position: absolute;
      top: 0; left: 0; right: 0;
      background: #b94040;
      color: #fff;
      font-size: .78rem;
      text-align: center;
      padding: 6px 12px;
      z-index: 30;
      transform: translateY(-100%);
      transition: transform .3s;
    }
    #offline-banner.show { transform: translateY(0); }

    /* ── Footer ───────────────────────────────────────── */
    footer {
      flex: 0 0 var(--footer-h);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      background: linear-gradient(0deg, var(--green-900), rgba(10,50,35,.9));
      border-top: 1px solid rgba(255,255,255,.07);
      font-size: .6rem;
      color: var(--text-dim);
      letter-spacing: .04em;
      padding-bottom: env(safe-area-inset-bottom);
    }
    footer a {
      color: var(--gold-dim);
      text-decoration: none;
    }
    footer a:hover { text-decoration: underline; }

    /* ── Install prompt ───────────────────────────────── */
    #install-toast {
      position: fixed;
      bottom: calc(var(--footer-h) + 12px + env(safe-area-inset-bottom));
      left: 50%;
      transform: translateX(-50%) translateY(20px);
      background: var(--green-700);
      border: 1px solid var(--gold);
      border-radius: var(--radius);
      padding: 12px 18px;
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: .8rem;
      box-shadow: var(--shadow);
      z-index: 50;
      opacity: 0;
      pointer-events: none;
      transition: opacity .3s, transform .3s;
      width: min(340px, 90vw);
    }
    #install-toast.show {
      opacity: 1;
      pointer-events: auto;
      transform: translateX(-50%) translateY(0);
    }
    #install-toast .toast-icon { font-size: 1.4rem; }
    #install-toast .toast-body { flex: 1; }
    #install-toast .toast-title { font-weight: 700; color: var(--white); margin-bottom: 2px; }
    #install-toast .toast-sub   { color: var(--text-dim); font-size: .7rem; }
    #btn-install {
      background: var(--gold);
      color: var(--green-900);
      border: none;
      border-radius: 8px;
      font-weight: 700;
      font-size: .75rem;
      padding: 7px 14px;
      cursor: pointer;
      white-space: nowrap;
      transition: background .2s;
    }
    #btn-install:hover { background: #ffe066; }
    #btn-dismiss {
      background: none;
      border: none;
      color: var(--text-dim);
      font-size: 1rem;
      cursor: pointer;
      padding: 4px;
    }
  </style>
</head>

<body>
<div id="app">

  <!-- ── Header ── -->
  <header>
    <img class="header-icon" src="./icons/icon-96x96.png" alt="停車場圖示" />
    <div>
      <div class="header-title">🅿️ 台南市停車場查詢</div>
      <div class="header-sub">資料來源：台南市政府開放資料平台</div>
    </div>
    <div class="header-spacer"></div>
    <div id="net-badge" class="online">
      <span id="net-dot"></span>
      <span id="net-label"></span>
    </div>
  </header>

  <!-- ── Main ── -->
  <main>
    <!-- Offline banner -->
    <div id="offline-banner">⚠️ 目前無網路連線，部分功能可能無法使用</div>

    <!-- Loading Splash -->
    <div id="splash">
      <img class="splash-logo" src="./icons/icon-192x192.png" alt="Logo" />
      <div class="splash-text">台南市停車場查詢</div>
      <div class="spinner"></div>
    </div>

    <!-- Gradio iframe -->
    <iframe
      id="parking-frame"
      src="https://cjhuang1681688-tainanparking.hf.space"
      title="台南市停車場查詢系統"
      allow="cross-origin-isolated"
      loading="lazy"
    ></iframe>
  </main>

  <!-- ── Footer ── -->
  <footer>
    <span>© 台南市政府開放資料</span>
    <span>·</span>
    <a href="https://data.tainan.gov.tw" target="_blank" rel="noopener">data.tainan.gov.tw</a>
    <span>·</span>
    <span id="app-ver">PWA v1.0</span>
  </footer>

</div>

<!-- ── Install Toast ── -->
<div id="install-toast">
  <span class="toast-icon">📲</span>
  <div class="toast-body">
    <div class="toast-title">安裝到主畫面</div>
    <div class="toast-sub">離線也能快速開啟</div>
  </div>
  <button id="btn-install">安裝</button>
  <button id="btn-dismiss" aria-label="關閉">✕</button>
</div>

<script>
  // ── Service Worker 註冊 ──────────────────────────────────
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./sw.js')
        .then(reg => console.log('[PWA] SW registered, scope:', reg.scope))
        .catch(err => console.warn('[PWA] SW registration failed:', err));
    });
  }

  // ── Splash 隱藏（iframe 載入後） ─────────────────────────
  const frame  = document.getElementById('parking-frame');
  const splash = document.getElementById('splash');

  // 逾時保護：最多等 12 秒
  const splashTimeout = setTimeout(() => splash.classList.add('hidden'), 12000);

  frame.addEventListener('load', () => {
    clearTimeout(splashTimeout);
    setTimeout(() => splash.classList.add('hidden'), 600);
  });

  // ── 網路狀態 ──────────────────────────────────────────────
  const netBadge      = document.getElementById('net-badge');
  const offlineBanner = document.getElementById('offline-banner');

  function updateNet() {
    const online = navigator.onLine;
    netBadge.className = online ? 'online' : 'offline';
    offlineBanner.classList.toggle('show', !online);
  }
  window.addEventListener('online',  updateNet);
  window.addEventListener('offline', updateNet);
  updateNet();

  // ── PWA Install Prompt ────────────────────────────────────
  let deferredPrompt = null;
  const toast      = document.getElementById('install-toast');
  const btnInstall = document.getElementById('btn-install');
  const btnDismiss = document.getElementById('btn-dismiss');

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // 延遲 3 秒顯示
    setTimeout(() => toast.classList.add('show'), 3000);
  });

  btnInstall.addEventListener('click', async () => {
    if (!deferredPrompt) return;
    toast.classList.remove('show');
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    console.log('[PWA] Install outcome:', outcome);
    deferredPrompt = null;
  });

  btnDismiss.addEventListener('click', () => {
    toast.classList.remove('show');
    deferredPrompt = null;
  });

  window.addEventListener('appinstalled', () => {
    console.log('[PWA] App installed!');
    toast.classList.remove('show');
  });
</script>
</body>
</html>
