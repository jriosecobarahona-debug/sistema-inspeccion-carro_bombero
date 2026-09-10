// Cambia 'v1' por 'v2' o superior
const CACHE_NAME = 'pwa-5ta-v2'; 

const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  './logo5ta.png'
];

// Evento Install: Fuerza al nuevo Service Worker a activarse de inmediato
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
});

// Evento Activate: Elimina cachés antiguas automáticamente
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});