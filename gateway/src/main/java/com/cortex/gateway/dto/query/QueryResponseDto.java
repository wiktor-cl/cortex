package com.cortex.gateway.dto.query;

import com.cortex.gateway.dto.query.ai.AiQueryResponse;
import java.util.List;
import java.util.UUID;

public record QueryResponseDto(
        UUID queryId, String answer, String mode, List<CitationDto> citations, List<SubAnswerDto> subAnswers) {
    public static QueryResponseDto from(UUID queryId, AiQueryResponse response) {
        return new QueryResponseDto(
                queryId,
                response.answer(),
                response.mode(),
                response.citations().stream().map(CitationDto::from).toList(),
                response.subAnswers().stream().map(SubAnswerDto::from).toList());
    }
}
