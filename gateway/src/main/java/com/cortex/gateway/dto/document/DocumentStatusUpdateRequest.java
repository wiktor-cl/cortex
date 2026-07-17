package com.cortex.gateway.dto.document;

import com.cortex.gateway.domain.DocumentStatus;
import jakarta.validation.constraints.NotNull;

/** Body of the worker's PATCH /internal/documents/{id}/status callback. */
public record DocumentStatusUpdateRequest(
        @NotNull DocumentStatus status, int chunkCount, String errorMessage) {}
