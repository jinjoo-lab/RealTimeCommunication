package com.example.realtimecommunication.module.location.service;

import com.example.realtimecommunication.module.location.dto.LocationDto;
import org.springframework.stereotype.Service;

@Service
public class LocationService {
    public LocationDto shareCurLocation() {
        return makeRandomLocation();
    }

    private LocationDto makeRandomLocation() {
        double landomX = Math.random() * 100;
        double landomY = Math.random() * 100;

        return new LocationDto(landomX,landomY);
    }
}
