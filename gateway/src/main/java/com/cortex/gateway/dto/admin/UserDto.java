package com.cortex.gateway.dto.admin;

import com.cortex.gateway.domain.Role;
import com.cortex.gateway.domain.User;
import java.time.Instant;
import java.util.UUID;

public record UserDto(UUID id, String email, Role role, Instant createdAt) {
    public static UserDto from(User user) {
        return new UserDto(user.getId(), user.getEmail(), user.getRole(), user.getCreatedAt());
    }
}
