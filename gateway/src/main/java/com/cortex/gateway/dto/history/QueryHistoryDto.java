package com.cortex.gateway.dto.history;

import com.cortex.gateway.dto.query.CitationDto;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

public record QueryHistoryDto(
        UUID id,
        UUID collectionId,
        String question,
        String answer,
        String mode,
        List<CitationDto> citations,
        Instant createdAt) {}
