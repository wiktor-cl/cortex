package com.cortex.gateway.security;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class RateLimiterTest {

    @Test
    void allowsUpToMaxRequestsWithinWindowThenRejects() {
        RateLimiter limiter = new RateLimiter(3, 60);

        assertThat(limiter.tryConsume("user:1")).isTrue();
        assertThat(limiter.tryConsume("user:1")).isTrue();
        assertThat(limiter.tryConsume("user:1")).isTrue();
        assertThat(limiter.tryConsume("user:1")).isFalse();
    }

    @Test
    void tracksSeparateKeysIndependently() {
        RateLimiter limiter = new RateLimiter(1, 60);

        assertThat(limiter.tryConsume("user:1")).isTrue();
        assertThat(limiter.tryConsume("user:2")).isTrue();
        assertThat(limiter.tryConsume("user:1")).isFalse();
    }

    @Test
    void resetsAfterWindowElapses() throws InterruptedException {
        RateLimiter limiter = new RateLimiter(1, 0);

        assertThat(limiter.tryConsume("user:1")).isTrue();
        Thread.sleep(5);
        assertThat(limiter.tryConsume("user:1")).isTrue();
    }
}
