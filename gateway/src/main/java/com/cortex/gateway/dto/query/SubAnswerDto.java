package com.cortex.gateway.dto.query;

import com.cortex.gateway.dto.query.ai.AiSubAnswer;
import java.util.List;

public record SubAnswerDto(String subQuestion, String toolUsed, String answer, List<CitationDto> citations) {
    public static SubAnswerDto from(AiSubAnswer subAnswer) {
        return new SubAnswerDto(
                subAnswer.subQuestion(),
                subAnswer.toolUsed(),
                subAnswer.answer(),
                subAnswer.citations().stream().map(CitationDto::from).toList());
    }
}
