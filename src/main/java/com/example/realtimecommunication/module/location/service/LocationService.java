package com.example.realtimecommunication.module.location.service;

import com.example.realtimecommunication.module.location.dto.LocationDto;

import org.springframework.stereotype.Service;
import org.springframework.web.context.request.async.DeferredResult;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.LinkedBlockingQueue;

@Service
public class LocationService {

    private static final long TIMEOUT = 10_000L;
    private final Map<Long, BlockingQueue<DeferredResult<LocationDto>>> groupRequests =
            new ConcurrentHashMap<>();

    public LocationDto shareCurLocation() {
        return makeRandomLocation();
    }

    private LocationDto makeRandomLocation() {
        double randomX = Math.random() * 100;
        double randomY = Math.random() * 100;

        return new LocationDto(randomX, randomY);
    }

    public DeferredResult<LocationDto> longPoll(final Long groupId) {
        final DeferredResult<LocationDto> deferredResult = new DeferredResult<>(TIMEOUT);

        deferredResult.onTimeout(() -> deferredResult.setErrorResult("Request timeout"));

        groupRequests
                .computeIfAbsent(groupId, k -> new LinkedBlockingQueue<>())
                .add(deferredResult);

        return deferredResult;
    }

    public void notifyGroup(final Long groupId) {
        final BlockingQueue<DeferredResult<LocationDto>> queue = groupRequests.get(groupId);

        Optional.ofNullable(queue)
                .ifPresent(
                        q -> {
                            while (!q.isEmpty()) {
                                q.poll().setResult(makeRandomLocation());
                            }
                        });
    }
}
