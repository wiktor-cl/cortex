package com.cortex.gateway.security;

import com.cortex.gateway.domain.Role;
import java.util.UUID;

/** The authenticated user, as carried on the Spring Security Authentication after JWT parsing. */
public record CortexPrincipal(UUID userId, String email, Role role) {}
