package com.example.realtimecommunication.module.location.service;

import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

@Service
public class SseService {

    private static final String SSE_EVENT_NAME = "location";
    private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();
    private final LocationService locationService;

    public SseService(final LocationService locationService) {
        this.locationService = locationService;
    }

    public SseEmitter add() {
        final SseEmitter emitter = new SseEmitter();
        this.emitters.add(emitter);

        emitter.onCompletion(() -> this.emitters.remove(emitter));
        emitter.onTimeout(emitter::complete);

        shareCurLocation();
        return emitter;
    }

    public void shareCurLocation() {
        emitters.forEach(
                emit -> {
                    try {
                        emit.send(
                                SseEmitter.event()
                                        .name(SSE_EVENT_NAME)
                                        .data(locationService.shareCurLocation()));
                    } catch (final IOException e) {
                        throw new RuntimeException(e);
                    }
                });
    }
}
