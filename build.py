#!/usr/bin/env python3
"""build worker.js from site/index.html + site/discoveries.html + site/discoveries.json.

the discoveries data lives in site/discoveries.json and is inlined into the
html at the /*__DISCOVERIES_JSON__*/ placeholder. the main page shows only the
latest discovery; /discoveries shows the full archive. the archive page reuses
the <style> block from index.html via the /*__ARCHIVE_STYLE__*/ placeholder.

pushing to main deploys via .github/workflows/deploy.yml, so the daily
discovery cron only needs to: append to discoveries.json, run this script,
commit, push.
"""
import json
import re

html = open('site/index.html').read()
discoveries = json.load(open('site/discoveries.json'))
# keep </script> from ever breaking out of the inline script tag
safe = json.dumps(discoveries).replace('</', '<\\/')
html = html.replace('/*__DISCOVERIES_JSON__*/[]', '/*__DISCOVERIES_JSON__*/' + safe)

# archive page: same styles, all discoveries newest-first
style = re.search(r'<style>.*?</style>', html, re.S).group(0)
archive = open('site/discoveries.html').read()
archive = archive.replace('/*__ARCHIVE_STYLE__*/', style)
archive = archive.replace('/*__DISCOVERIES_JSON__*/[]', '/*__DISCOVERIES_JSON__*/' + safe)

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
    var path = url.pathname;
    var headers = { "content-type": "text/html;charset=UTF-8", "cache-control": "public, max-age=300" };
    if (path === "/" || path === "/index.html") {
      return new Response(HTML, { headers: headers });
    }
    if (path === "/discoveries" || path === "/discoveries.html") {
      return new Response(ARCHIVE_HTML, { headers: headers });
    }
    return new Response("not found :( \\\\u2026 try /", { status: 404, headers: { "content-type": "text/plain" } });
  }
};

var HTML = ''' + json.dumps(html) + ''';
var ARCHIVE_HTML = ''' + json.dumps(archive) + ''';
'''
open('worker.js', 'w').write(js)
print('built worker.js from site/index.html + site/discoveries.html + site/discoveries.json')
