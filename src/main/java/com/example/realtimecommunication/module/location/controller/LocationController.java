package com.example.realtimecommunication.module.location.controller;

import com.example.realtimecommunication.module.location.service.LocationService;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class LocationController {
    private final LocationService locationService;

    public LocationController(LocationService locationService) {
        this.locationService = locationService;
    }
}
