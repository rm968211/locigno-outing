/* Network-first everywhere, cache as fallback — Ryan updates the page and
   the assets by pushing to the repo, so fresh content always wins when
   online and the last-seen version still loads on the course with no bars. */
const CACHE = "locigno-v1";
const SHELL = ["./", "index.html", "manifest.webmanifest", "assets/cross-creek-logo.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    /* no-cache: always revalidate with the server instead of trusting the
       local HTTP cache — a pushed update reaches clients on their next load */
    fetch(e.request, { cache: "no-cache" }).then(res => {
      if (res.ok) {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return res;
    }).catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
