package com.example.realtimecommunication.module.location.controller;

import com.example.realtimecommunication.module.location.service.LocationService;

import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;

@Controller
public class StompController {

    private final SimpMessagingTemplate template;
    private final LocationService locationService;

    public StompController(
            final SimpMessagingTemplate template, final LocationService locationService) {
        this.template = template;
        this.locationService = locationService;
    }

    @MessageMapping("/share/{id}")
    public void shareCurLocationByStomp(@DestinationVariable final Long id) {
        template.convertAndSend(
                String.format("/sub/location/%d", id), locationService.shareCurLocation());
    }
}
