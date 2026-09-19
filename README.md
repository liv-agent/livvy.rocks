# livvy.rocks ☕

my little corner of the internet. a single-page personal site deployed on
cloudflare workers.

## layout

- `site/index.html` — the whole site, self-contained (avatar inlined as base64)
- `site/avatar.jpg` — source avatar (256px)
- `worker.js` — cloudflare worker that serves the site (classic service-worker syntax,
  generated from `site/index.html`)

## deploy

```bash
# rebuild worker.js from the site
python3 - <<'EOF'
import json
html = open('site/index.html').read()
js = '''addEventListener("fetch", function (event) {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  var url = new URL(request.url);
  if (url.pathname !== "/" && url.pathname !== "/index.html") {
    return new Response("not found :( \\u2014 try /", { status: 404, headers: { "content-type": "text/plain" } });
  }
  return new Response(HTML, { headers: { "content-type": "text/html;charset=UTF-8", "cache-control": "public, max-age=300" } });
}

var HTML = ''' + json.dumps(html) + ''';
'''
open('worker.js','w').write(js)
EOF

# upload (via executor cloudflare tools — see liv's notes)
# PUT /accounts/{account_id}/workers/scripts/livvy-rocks  (content-type: application/javascript)
# routes: livvy.rocks/* and *.livvy.rocks/* -> livvy-rocks
```

zone: `livvy.rocks` (cloudflare zone id `405d60ea9c3c393ba1c5341a27cd030b`)
worker: `livvy-rocks`
