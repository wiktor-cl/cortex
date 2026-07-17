package com.cortex.gateway.dto.query;

import com.cortex.gateway.dto.query.ai.AiCitation;
import java.util.UUID;

public record CitationDto(
        UUID documentId, String filename, Integer pageNumber, int chunkIndex, String snippet, double score) {
    public static CitationDto from(AiCitation citation) {
        return new CitationDto(
                citation.documentId(),
                citation.filename(),
                citation.pageNumber(),
                citation.chunkIndex(),
                citation.snippet(),
                citation.score());
    }
}
