package com.cortex.gateway.dto.query.ai;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import java.util.UUID;

/** Mirrors ai-service's POST /query request body (snake_case wire format - see ai-service's
 * app/schemas.py QueryRequest). Kept separate from the gateway's own public QueryRequestDto so
 * each service's wire format can evolve independently. */
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record AiQueryRequest(String question, UUID collectionId, int topK) {}
