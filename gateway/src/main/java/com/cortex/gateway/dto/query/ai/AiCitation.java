package com.cortex.gateway.dto.query.ai;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import java.util.UUID;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record AiCitation(
        UUID documentId, String filename, Integer pageNumber, int chunkIndex, String snippet, double score) {}
