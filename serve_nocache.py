#!/usr/bin/env python3
"""带合理缓存策略的静态服务器：HTML 协商缓存，静态素材长期缓存。"""
import functools
import http.server
import os
import socketserver

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 6200


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 页面主入口和逻辑脚本不强制缓存，保证修改实时生效
        path = self.path.split("?")[0]
        if path.endswith(".html") or path == "/" or path.endswith(".js"):
            self.send_header("Cache-Control", "no-cache, must-revalidate")
        elif path.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff2", ".ttf")):
            # 贴图、音频、字体等静态大文件缓存 7 天，手机不用每次都重下几十张图
            self.send_header("Cache-Control", "public, max-age=604800, immutable")
        else:
            self.send_header("Cache-Control", "public, max-age=3600")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 128


if __name__ == "__main__":
    handler = functools.partial(Handler, directory=ROOT)
    with Server(("0.0.0.0", PORT), handler) as httpd:
        httpd.serve_forever()
