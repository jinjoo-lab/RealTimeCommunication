package com.example.realtimecommunication.module.location.controller;

import com.example.realtimecommunication.module.location.dto.LocationDto;
import com.example.realtimecommunication.module.location.service.LocationService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController("/location")
public class LocationController {
    private final LocationService locationService;

    public LocationController(LocationService locationService) {
        this.locationService = locationService;
    }

    @GetMapping("/cur")
    public ResponseEntity<LocationDto> shareCurLocation() {
        return ResponseEntity.ok(locationService.shareCurLocation());
    }
}
