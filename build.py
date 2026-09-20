#!/usr/bin/env python3
"""build worker.js from site/index.html + site/discoveries.json.

the discoveries section of the page is fed by site/discoveries.json, which is
inlined into the html at the /*__DISCOVERIES_JSON__*/ placeholder. pushing to
main deploys via .github/workflows/deploy.yml, so the daily discovery cron only
needs to: append to discoveries.json, run this script, commit, push.
"""
import json

html = open('site/index.html').read()
discoveries = json.load(open('site/discoveries.json'))
# keep </script> from ever breaking out of the inline script tag
safe = json.dumps(discoveries).replace('</', '<\\/')
html = html.replace('/*__DISCOVERIES_JSON__*/[]', '/*__DISCOVERIES_JSON__*/' + safe)

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
open('worker.js', 'w').write(js)
print('built worker.js from site/index.html + site/discoveries.json')
