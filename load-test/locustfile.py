import random
import threading

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
    host = "http://localhost:8080"
    ws = None

    def on_start(self):
        self.ws = WebSocketApp("ws://localhost:8080/ws")
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()

    @task
    def websocket_task(self):
        self.ws.send("WebSocket Test Message")


class STOMP(HttpUser):
    wait_time = between(2.5, 3.5)
    host = "http://localhost:8080"
    conn = None
    group_id = random.randint(1, 10)

    def on_start(self):
        self.conn = Connection([('localhost', 8080)])
        self.conn.set_listener('', PrintingListener())
        self.conn.connect('user', 'pass', wait=True)
        self.conn.subscribe(f'/sub/location/{self.group_id}', id=f"{self.group_id}", ack='auto')

    @task
    def stomp_task(self):
        self.conn.send(body='STOMP Test Message', destination=f'/pub/share/{self.group_id}')
