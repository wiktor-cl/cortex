package com.cortex.gateway.security;

import com.cortex.gateway.domain.Role;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.Date;
import java.util.UUID;
import javax.crypto.SecretKey;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class JwtService {

    private final SecretKey signingKey;
    private final Duration tokenValidity;

    public JwtService(
            @Value("${cortex.jwt.secret}") String secret,
            @Value("${cortex.jwt.validity-minutes:60}") long validityMinutes) {
        this.signingKey = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.tokenValidity = Duration.ofMinutes(validityMinutes);
    }

    public String generateToken(UUID userId, String email, Role role) {
        Instant now = Instant.now();
        return Jwts.builder()
                .subject(userId.toString())
                .claim("email", email)
                .claim("role", role.name())
                .issuedAt(Date.from(now))
                .expiration(Date.from(now.plus(tokenValidity)))
                .signWith(signingKey)
                .compact();
    }

    /** Returns empty if the token is missing, malformed, expired, or signed with a different key. */
    public java.util.Optional<Claims> parseClaims(String token) {
        try {
            return java.util.Optional.of(
                    Jwts.parser().verifyWith(signingKey).build().parseSignedClaims(token).getPayload());
        } catch (JwtException | IllegalArgumentException exception) {
            return java.util.Optional.empty();
        }
    }

    public UUID extractUserId(Claims claims) {
        return UUID.fromString(claims.getSubject());
    }

    public Role extractRole(Claims claims) {
        return Role.valueOf(claims.get("role", String.class));
    }

    public String extractEmail(Claims claims) {
        return claims.get("email", String.class);
    }
}
