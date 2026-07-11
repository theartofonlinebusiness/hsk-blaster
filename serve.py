import http.server, socketserver, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
PORT=7777
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
with socketserver.TCPServer(('',PORT),H) as s:
    s.serve_forever()
