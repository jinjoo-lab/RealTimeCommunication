import {check, sleep} from 'k6';
import http from 'k6/http';
import ws from 'k6/ws';

let longPollingConnection = null;
let sseConnection = null;
let websocketConnection = null;
let stompClient = null;

export let options = {
    stages: [
        {duration: '20s', target: 20},
        {duration: '30s', target: 90},
        {duration: '10s', target: 0},
    ],
};

const baseUrl = 'http://localhost:8080';
const wsUrl = 'ws://localhost:8080/ws';
const stompUrl = 'ws://localhost:8080/location';
const randomInt = getRandomInt();

function getRandomInt() {
    return Math.floor(Math.random() * 10) + 1;
}

function shortPollingTest() {
    http.get(`http://localhost:8080/cur/${randomInt}`);
}

function initializeLongPollingConnection() {
    if (longPollingConnection) {
        return longPollingConnection;
    }

    const connection = http.get(`${baseUrl}/location/long/${randomInt}`, {
        headers: {Accept: 'text/event-stream'},
        tags: {type: 'longPolling'}
    });
    check(connection, {'Long Polling Connection Status is 200': (r) => r.status === 200});
    return connection;
}

function initializeSSEConnection() {
    if (sseConnection) {
        return sseConnection;
    }
    const connection = http.get(`${baseUrl}/location/sse/connect`, {
        headers: {Accept: 'text/event-stream'},
        tags: {type: 'sse'}
    });
    check(connection, {'SSE Connection Status is 200': (r) => r.status === 200});
    return connection;
}

function initializeWebSocketConnection() {
    if (websocketConnection) {
        return websocketConnection;
    }

    const connection = ws.connect(wsUrl, function (socket) {
        socket.on('open', function () {
            socket.send('Hello from k6 WebSocket!');
        });

        socket.on('message', function (message) {
        });

        socket.on('close', function () {
        });
    });

    websocketConnection = connection;
    return connection;
}

function initializeStompClient() {
    if (stompClient) {
        return stompClient;
    }

    const client = ws.connect(stompUrl, function (socket) {
        socket.on('open', function () {
            socket.send('CONNECT\naccept-version:1.0,1.1,2.0\n\n\x00\n');
            socket.send(`SUBSCRIBE\nid:${randomInt}\ndestination:/sub/location/${randomInt}\n\n\x00\n`);
        });

        socket.on('message', function (message) {
        });

        socket.on('close', function () {
        });
    });

    stompClient = client;
    return client;
}

export default function () {
    // shortPollingTest();
    // longPollingTest();
    // sseTest();
    // websocketTest();
    stompTest();

    sleep(3);
}

export function longPollingTest() {
    initializeLongPollingConnection();
    const url = `${baseUrl}/location/long/${randomInt}`;
    const response = http.get(url);
    check(response, {'Long Polling Post Status is 200': (r) => r.status === 200});

    const notifyResponse = http.post(`${baseUrl}/location/long/${randomInt}/notify`);
    check(notifyResponse, {'Long Polling Notify Status is 200': (r) => r.status === 200});
}

export function sseTest() {
    initializeSSEConnection();
    const postResponse = http.post(`${baseUrl}/location/sse/share`);
    check(postResponse, {'SSE Share Status is 200': (r) => r.status === 200});
}

export function websocketTest() {
    initializeWebSocketConnection();
    ws.connect(wsUrl, function (socket) {
        socket.on('open', function () {
            socket.send('Hello from k6!');
        });
    });
}

export function stompTest() {
    initializeStompClient();
    stompClient.on('open', function () {
        stompClient.send(`SEND\ndestination:/pub/share/${randomInt}\n\n${JSON.stringify({content: 'Hi from k6 STOMP!'})}\x00\n`);
    });
}
