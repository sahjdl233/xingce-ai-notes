#!/usr/bin/env python3
import json
import sys
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8000


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("[preview] %s\n" % (fmt % args))

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404, "Not Found")
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            self._json({"error": "请求体不是有效 JSON"}, 400)
            return
        base_url = str(body.get("baseUrl", "")).strip().rstrip("/")
        model = str(body.get("model", "")).strip()
        if not base_url or not model:
            self._json({"error": "缺少 baseUrl 或 model"}, 400)
            return
        payload = {
            "model": model,
            "messages": body.get("messages"),
            "temperature": body.get("temperature", 0.2),
        }
        headers = {"Content-Type": "application/json"}
        api_key = str(body.get("apiKey", "")).strip()
        if api_key:
            headers["Authorization"] = "Bearer " + api_key
        req = urllib.request.Request(
            base_url + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = resp.read().decode("utf-8", errors="replace")
                self.send_response(resp.status)
                ctype = resp.headers.get("Content-Type", "application/json")
                self.send_header("Content-Type", ctype)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data.encode("utf-8"))
        except urllib.error.HTTPError as e:
            data = e.read().decode("utf-8", errors="replace")
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "application/json"))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data.encode("utf-8"))
        except Exception as e:
            self._json({"error": "转发失败: " + str(e)}, 502)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _json(self, obj, status):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print("preview server on http://0.0.0.0:%d root=%s" % (PORT, ROOT), flush=True)
    server.serve_forever()
