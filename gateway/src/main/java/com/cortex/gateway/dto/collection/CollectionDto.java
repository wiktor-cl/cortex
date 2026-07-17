package com.cortex.gateway.dto.collection;

import com.cortex.gateway.domain.DocumentCollection;
import java.time.Instant;
import java.util.UUID;

public record CollectionDto(UUID id, String name, String description, UUID ownerId, Instant createdAt) {
    public static CollectionDto from(DocumentCollection collection) {
        return new CollectionDto(
                collection.getId(),
                collection.getName(),
                collection.getDescription(),
                collection.getOwnerId(),
                collection.getCreatedAt());
    }
}
