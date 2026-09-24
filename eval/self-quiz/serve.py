#!/usr/bin/env python3
"""自测页 server：静态文件 + POST /answer 追加写 results.jsonl。

用法: python3 eval/self-quiz/serve.py  →  http://127.0.0.1:8767/
"""
import json
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
RESULTS = HERE / "results.jsonl"
PORT = 8767


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(HERE), **kw)

    def log_message(self, fmt, *args):
        pass

    def do_POST(self):
        if self.path != "/answer":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length", 0))
        try:
            rec = json.loads(self.rfile.read(n))
            assert rec["card_id"] and rec["choice"] in (1, 2, 3, 4)
        except Exception:
            self.send_error(400)
            return
        rec["server_ts"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        with RESULTS.open("a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self.send_response(204)
        self.end_headers()


if __name__ == "__main__":
    print(f"KB 熟悉度自测 → http://127.0.0.1:{PORT}/")
    print(f"结果文件 → {RESULTS}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
