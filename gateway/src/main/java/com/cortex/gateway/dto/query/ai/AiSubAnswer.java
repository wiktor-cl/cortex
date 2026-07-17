package com.cortex.gateway.dto.query.ai;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import java.util.List;

@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record AiSubAnswer(String subQuestion, String toolUsed, String answer, List<AiCitation> citations) {}
