import random
import stomper
import json
import time

from locust import events
from locust import HttpUser, User, task, between
from websocket import create_connection


class SSE(HttpUser): # 1700
    wait_time = between(2.5, 3.5)
    host = "http://localhost:8080"

    def on_start(self):
        self.client.get("/location/sse/connect", stream=True)

    @task
    def sse_task(self):
        self.client.post("/location/sse/share")
        self.client.get("/location/sse/connect", stream=True)

class LongPolling(HttpUser): # 2500
    wait_time = between(2.5, 3.5)
    host = "http://localhost:8080"

    def on_start(self):
        self.client.get(f"/location/long/{random.randint(1, 10)}", stream=True)

    @task
    def long_polling_task(self):
        self.client.post(f"/location/long/{random.randint(1, 10)}/notify")

class ShortPolling(HttpUser): # 1900 (요동이 많이 침)
    wait_time = between(2.5, 3.5)
    host = "http://localhost:8080"

    @task
    def short_polling_task(self):
        self.client.get("/location/cur")

class WebSocket(User):
    wait_time = between(2.5, 3.5)
    host = "ws://localhost:8080/ws"
    ws = None

    def on_start(self):
        self.connect()

    def connect(self):
        try:
            self.ws = create_connection(self.host)
        except Exception as e:
            pass

    @task
    def send_message(self):
        try:
            if self.ws and self.ws.connected:
                self.ws.send("Hello from Locust!")
                response = self.ws.recv()
            else:
                self.connect()
        except WebSocketConnectionClosedException as e:
            self.connect()

    def on_stop(self):
        if self.ws and self.ws.connected:
            self.ws.close()
            print("WebSocket 연결 종료")

class STOMP(HttpUser): # 2700
    wait_time = between(2.5, 3.5)
    host = "ws://localhost:8080/location"

    def on_start(self):
        self.stompClient = StompClient()
        self.stompClient.connect()
        self.stompClient.subscribe()

    @task
    def stomp_task(self):
        self.stompClient.send({"content":"Hi!"}, '')


class StompClient(object):
    wait_time = between(2.5, 3.5)
    host = "localhost"
    port = 8080
    endpoint = "location"
    group_id = None
    ws = None

    def __init__(self):
        self.ws_uri = f"ws://{self.host}:{self.port}/{self.endpoint}"
        self.group_id = random.randint(1, 10)

    def on_start(self):
        try:
            self.connect()
            self.subscribe()
        except Exception as e:
            self.log_error("Failed to connect or subscribe: %s" % str(e))
            events.request.fire(request_type="stomp", name="connect", response_time=0, exception=e, response_length=0)

    def on_stop(self):
        self.close()

    def connect(self):
        start_time = time.time()
        try:
            self.ws = create_connection(self.ws_uri)
            self.ws.send("CONNECT\naccept-version:1.0,1.1,2.0\n\n\x00\n")
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(request_type="stomp", name="connect", response_time=total_time, exception=e , response_length=0)
            raise e
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(request_type="stomp", name="connect", response_time=total_time, response_length=0)

    def subscribe(self):
        start_time = time.time()
        try:
            self.ws.send(f"SUBSCRIBE\nid:{self.group_id}\ndestination:/sub/location/{self.group_id}\n\n\x00\n")
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(request_type="stomp", name="subscribe", response_time=total_time, exception=e , response_length=0)
            raise e
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(request_type="stomp", name="subscribe", response_time=total_time, response_length=0)


    def close(self):
        if self.ws:
            self.ws.close()

    @task
    def stomp_task(self):
        self.send(body='STOMP Test Message', destination=f'/pub/share/{self.group_id}')

    def send(self, body, destination):
        start_time = time.time()
        try:
            msg = stomper.Frame()
            msg.cmd = 'SEND'
            msg.headers = {'destination': f'/pub/share/{self.group_id}'}
            msg.body = json.dumps(body)
            self.ws.send(msg.pack())
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(request_type="stomp", name="send", response_time=total_time, exception=e , response_length=0)
            raise e
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(request_type="stomp", name="send", response_time=total_time, response_length=0)
