# livvy.rocks ☕

my little corner of the internet. a single-page personal site deployed on
cloudflare workers.

## layout

- `site/index.html` — the whole site, self-contained (avatar inlined as base64)
- `site/avatar.jpg` - source avatar (256px)
- `worker.js` - cloudflare worker that serves the site (es-module syntax,
  generated from `site/index.html`; includes the `/api/brews` KV counter)

## persistence

the "brew me a coffee" counter lives in a cloudflare KV namespace:

- namespace: `livvy-brews` (`725604c66e704248a0dee78309795484`)
- binding: `BREWS` → key `count`
- `GET /api/brews` → `{ "count": n }`
- `POST /api/brews` → increments, returns `{ "count": n }`

the frontend falls back to localStorage if the api is unreachable.

## deploy

```bash
# rebuild worker.js from the site
python3 - <<'EOF'
import json
html = open('site/index.html').read()
js = '''export default {
  async fetch(request, env) {
    var url = new URL(request.url);
    if (url.pathname === "/api/brews") {
      var kv = env.BREWS;
      if (request.method === "GET") {
        var count = parseInt((await kv.get("count")) || "0", 10);
        return Response.json({ count: count });
      }
      if (request.method === "POST") {
        var next = parseInt((await kv.get("count")) || "0", 10) + 1;
        await kv.put("count", String(next));
        return Response.json({ count: next });
      }
      return new Response("method not allowed", { status: 405 });
    }
    if (url.pathname !== "/" && url.pathname !== "/index.html") {
      return new Response("not found :( \\\\u2026 try /", { status: 404, headers: { "content-type": "text/plain" } });
    }
    return new Response(HTML, { headers: { "content-type": "text/html;charset=UTF-8", "cache-control": "public, max-age=300" } });
  }
};

var HTML = ''' + json.dumps(html) + ''';
'''
open('worker.js','w').write(js)
EOF

# upload (multipart: metadata includes the KV binding)
# PUT /accounts/{account_id}/workers/scripts/livvy-rocks
#   metadata: {"main_module":"worker.js","compatibility_date":"2026-09-19",
#              "bindings":[{"type":"kv_namespace","name":"BREWS","namespace_id":"725604c66e704248a0dee78309795484"}]}
#   worker.js: application/javascript+module
# routes: livvy.rocks/* and *.livvy.rocks/* -> livvy-rocks
# (pushing to main also deploys via .github/workflows/deploy.yml → wrangler)
```

zone: `livvy.rocks` (cloudflare zone id `405d60ea9c3c393ba1c5341a27cd030b`)
worker: `livvy-rocks`
