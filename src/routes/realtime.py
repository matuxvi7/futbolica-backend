from flask_sock import Sock


def register_realtime_routes(sock: Sock) -> None:
    @sock.route("/ws/health")
    def websocket_health(ws):
        ws.send('{"status":"ok","service":"futbolica-backend"}')