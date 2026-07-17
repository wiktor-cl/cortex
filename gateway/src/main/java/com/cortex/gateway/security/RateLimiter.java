package com.cortex.gateway.security;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * Fixed-window rate limiter, keyed per caller (authenticated user id, or IP for anonymous
 * requests). Deliberately in-memory rather than Redis-backed: the gateway runs as a single
 * instance in this deployment (see docker-compose.yml), so a distributed limiter would add
 * complexity without a real benefit - documented as a scaling trade-off in ARCHITECTURE.md.
 */
@Component
public class RateLimiter {

    private record Window(AtomicInteger count, AtomicLong windowStartMillis) {}

    private final Map<String, Window> windows = new ConcurrentHashMap<>();
    private final int maxRequests;
    private final long windowMillis;

    public RateLimiter(
            @Value("${cortex.rate-limit.max-requests:60}") int maxRequests,
            @Value("${cortex.rate-limit.window-seconds:60}") long windowSeconds) {
        this.maxRequests = maxRequests;
        this.windowMillis = windowSeconds * 1000;
    }

    public boolean tryConsume(String key) {
        long now = System.currentTimeMillis();
        Window window = windows.computeIfAbsent(key, k -> new Window(new AtomicInteger(0), new AtomicLong(now)));
        synchronized (window) {
            if (now - window.windowStartMillis().get() >= windowMillis) {
                window.windowStartMillis().set(now);
                window.count().set(0);
            }
            if (window.count().get() >= maxRequests) {
                return false;
            }
            window.count().incrementAndGet();
            return true;
        }
    }
}
