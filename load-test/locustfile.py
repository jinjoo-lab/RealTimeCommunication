import random

from locust import HttpUser, task, between
from stomp import Connection, PrintingListener
from websocket import WebSocketApp

class SSE(HttpUser):
    wait_time = between(2.5, 3.5)
    host = "http://localhost:8080"

    def on_start(self):
        self.client.get("/location/sse/connect", stream=True)

    @task
    def sse_task(self):
        self.client.post("/location/sse/share")

class LongPolling(HttpUser):
    wait_time = between(2.5, 3.5)
    host = "http://localhost:8080"
    group_id = random.randint(1, 10)

    def on_start(self):
        self.client.get(f"/location/long/{self.group_id}")

    @task
    def long_polling_task(self):
        self.client.post(f"/location/long/{self.group_id}/notify")

class ShortPolling(HttpUser):
    wait_time = between(2.5, 3.5)
    host = "http://localhost:8080"

    @task
    def short_polling_task(self):
        self.client.get("/location/cur")

class WebSocket(HttpUser):
    wait_time = between(2.5, 3.5)
    host = "ws://localhost:8080"
    ws = None

    def on_start(self):
        self.setup_websocket()

    def setup_websocket(self):
        self.ws = WebSocketApp("ws://localhost:8080/ws", on_close=self.on_close)

    @task
    def websocket_task(self):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.send("message")
            return
        self.setup_websocket()
        self.ws.send("message")
    

    def on_close(self):
        self.setup_websocket()

class STOMP(HttpUser):
    wait_time = between(2.5, 3.5)
    host = "localhost"
    conn = None
    group_id = None

    def on_start(self):
        self.group_id = random.randint(1, 10)
        self.conn = Connection([('localhost', 8080)])
        self.conn.set_listener('', PrintingListener())
        self.conn.connect('user', 'pass', wait=True)
        self.conn.subscribe(f'/sub/location/{self.group_id}', id=f"{self.group_id}", ack='auto')

    @task
    def stomp_task(self):
        self.conn.send(body='STOMP Test Message', destination=f'/pub/share/{self.group_id}')
