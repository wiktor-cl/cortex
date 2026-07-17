package com.cortex.gateway.dto.auth;

import com.cortex.gateway.domain.Role;
import java.util.UUID;

public record AuthResponse(String token, UUID userId, String email, Role role) {}
