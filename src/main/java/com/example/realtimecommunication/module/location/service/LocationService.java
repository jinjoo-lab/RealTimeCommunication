package com.example.realtimecommunication.module.location.service;

import com.example.realtimecommunication.module.location.dto.LocationDto;

import org.springframework.stereotype.Service;

@Service
public class LocationService {
    public LocationDto shareCurLocation() {
        return makeRandomLocation();
    }

    private LocationDto makeRandomLocation() {
        double randomX = Math.random() * 100;
        double randomY = Math.random() * 100;

        return new LocationDto(randomX, randomY);
    }
}
