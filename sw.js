/**
 * sw.js — Service Worker for 台南市停車場查詢 PWA
 *
 * 策略：
 *  - App Shell (index.html / manifest / icons) → Cache First（離線仍可啟動）
 *  - Gradio API 及外部資源 → Network First（優先即時資料，失敗才回 cache）
 */

const CACHE_NAME   = 'tainan-parking-v1';
const STATIC_CACHE = 'tainan-parking-static-v1';

/** 預先快取的 App Shell 資源 */
const PRECACHE_URLS = [
  './index.html',
  './manifest.json',
  './icons/icon-192x192.png',
  './icons/icon-512x512.png',
  './icons/apple-touch-icon.png',
];

// ── Install ────────────────────────────────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[SW] Pre-caching App Shell');
      return cache.addAll(PRECACHE_URLS);
    })
  );
  self.skipWaiting();
});

// ── Activate ───────────────────────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  const VALID = [CACHE_NAME, STATIC_CACHE];
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => !VALID.includes(k))
          .map((k) => {
            console.log('[SW] Deleting old cache:', k);
            return caches.delete(k);
          })
      )
    )
  );
  self.clients.claim();
});

// ── Fetch ──────────────────────────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 僅處理 http / https
  if (!url.protocol.startsWith('http')) return;

  // ① App Shell → Cache First
  if (isAppShell(url)) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // ② Gradio / HuggingFace API → Network First（停車即時資料）
  if (url.hostname.includes('hf.space') || url.hostname.includes('huggingface.co')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // ③ 其餘靜態資源 → Stale-While-Revalidate
  event.respondWith(staleWhileRevalidate(request));
});

// ── 策略函式 ────────────────────────────────────────────────────────────────

function isAppShell(url) {
  return PRECACHE_URLS.some((p) => url.pathname.endsWith(p.replace('./', '/')));
}

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(STATIC_CACHE);
    cache.put(request, response.clone());
  }
  return response;
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    // 離線且無 cache：回傳友善提示
    return new Response(
      JSON.stringify({ error: '目前離線，請確認網路連線後再試。' }),
      { headers: { 'Content-Type': 'application/json' } }
    );
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) cache.put(request, response.clone());
    return response;
  });
  return cached || fetchPromise;
}

// ── Push 通知（預留擴充） ────────────────────────────────────────────────────
self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? { title: '台南停車場', body: '有新通知' };
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: './icons/icon-192x192.png',
      badge: './icons/icon-72x72.png',
    })
  );
});
