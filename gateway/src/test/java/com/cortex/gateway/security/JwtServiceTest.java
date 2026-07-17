package com.cortex.gateway.security;

import static org.assertj.core.api.Assertions.assertThat;

import com.cortex.gateway.domain.Role;
import io.jsonwebtoken.Claims;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class JwtServiceTest {

    private final JwtService jwtService =
            new JwtService("test-secret-key-that-is-long-enough-for-hs256-signing", 60);

    @Test
    void generatesTokenThatRoundTripsAllClaims() {
        UUID userId = UUID.randomUUID();
        String token = jwtService.generateToken(userId, "alice@example.com", Role.ADMIN);

        Optional<Claims> claims = jwtService.parseClaims(token);

        assertThat(claims).isPresent();
        assertThat(jwtService.extractUserId(claims.get())).isEqualTo(userId);
        assertThat(jwtService.extractEmail(claims.get())).isEqualTo("alice@example.com");
        assertThat(jwtService.extractRole(claims.get())).isEqualTo(Role.ADMIN);
    }

    @Test
    void rejectsMalformedToken() {
        assertThat(jwtService.parseClaims("not-a-real-jwt")).isEmpty();
    }

    @Test
    void rejectsTokenSignedWithDifferentKey() {
        JwtService otherService =
                new JwtService("a-completely-different-secret-key-thats-also-long-enough", 60);
        String token = otherService.generateToken(UUID.randomUUID(), "bob@example.com", Role.USER);

        assertThat(jwtService.parseClaims(token)).isEmpty();
    }
}
