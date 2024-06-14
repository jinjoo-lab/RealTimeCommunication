package com.example.realtimecommunication.config;

import com.example.realtimecommunication.module.location.dto.LocationDto;
import com.example.realtimecommunication.module.location.service.LocationService;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

@Component
@Slf4j
public class CustomWebSocketHandler extends TextWebSocketHandler {

    private final ObjectMapper objectMapper;
    private final LocationService locationService;
    private final Set<WebSocketSession> sessions = ConcurrentHashMap.newKeySet();

    public CustomWebSocketHandler(LocationService locationService, ObjectMapper objectMapper) {
        this.locationService = locationService;
        this.objectMapper = objectMapper;
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        log.info("HANDLE WEBSOCKET MESSAGE");
        LocationDto location = locationService.shareCurLocation();

        session.sendMessage(new TextMessage(objectMapper.writeValueAsString(location)));
    }

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        log.info("WEBSOCKET CONNECT");
        sessions.add(session);
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        log.info("WEBSOCKET DISCONNECT");
        sessions.remove(session);
    }
}
