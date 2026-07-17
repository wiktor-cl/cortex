package com.cortex.gateway.dto.document;

import com.cortex.gateway.domain.DocumentEntity;
import com.cortex.gateway.domain.DocumentStatus;
import java.time.Instant;
import java.util.UUID;

public record DocumentDto(
        UUID id,
        UUID collectionId,
        String filename,
        UUID uploadedBy,
        DocumentStatus status,
        int chunkCount,
        String errorMessage,
        Instant uploadedAt) {
    public static DocumentDto from(DocumentEntity entity) {
        return new DocumentDto(
                entity.getId(),
                entity.getCollectionId(),
                entity.getFilename(),
                entity.getUploadedBy(),
                entity.getStatus(),
                entity.getChunkCount(),
                entity.getErrorMessage(),
                entity.getUploadedAt());
    }
}
