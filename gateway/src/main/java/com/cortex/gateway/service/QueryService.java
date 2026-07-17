package com.cortex.gateway.service;

import com.cortex.gateway.domain.QueryHistoryEntity;
import com.cortex.gateway.dto.query.QueryRequestDto;
import com.cortex.gateway.dto.query.QueryResponseDto;
import com.cortex.gateway.dto.query.ai.AiQueryRequest;
import com.cortex.gateway.dto.query.ai.AiQueryResponse;
import com.cortex.gateway.dto.history.QueryHistoryDto;
import com.cortex.gateway.exception.AiServiceException;
import com.cortex.gateway.repository.QueryHistoryRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientException;

@Service
public class QueryService {

    private final WebClient aiServiceWebClient;
    private final QueryHistoryRepository queryHistoryRepository;
    private final ObjectMapper objectMapper;

    public QueryService(
            WebClient aiServiceWebClient, QueryHistoryRepository queryHistoryRepository, ObjectMapper objectMapper) {
        this.aiServiceWebClient = aiServiceWebClient;
        this.queryHistoryRepository = queryHistoryRepository;
        this.objectMapper = objectMapper;
    }

    public QueryResponseDto ask(UUID userId, QueryRequestDto request) {
        int topK = request.topK() != null ? request.topK() : 5;
        AiQueryRequest aiRequest = new AiQueryRequest(request.question(), request.collectionId(), topK);

        AiQueryResponse aiResponse;
        try {
            aiResponse = aiServiceWebClient
                    .post()
                    .uri("/query")
                    .bodyValue(aiRequest)
                    .retrieve()
                    .bodyToMono(AiQueryResponse.class)
                    .block();
        } catch (WebClientException exception) {
            throw new AiServiceException("Failed to reach ai-service", exception);
        }
        if (aiResponse == null) {
            throw new AiServiceException("ai-service returned an empty response", null);
        }

        UUID queryId = UUID.randomUUID();
        QueryHistoryEntity history = new QueryHistoryEntity(
                userId,
                request.collectionId(),
                request.question(),
                aiResponse.answer(),
                aiResponse.mode(),
                serializeCitations(aiResponse));
        queryHistoryRepository.save(history);

        return QueryResponseDto.from(queryId, aiResponse);
    }

    public List<QueryHistoryDto> history(UUID userId) {
        return queryHistoryRepository.findByUserIdOrderByCreatedAtDesc(userId).stream()
                .map(this::toHistoryDto)
                .toList();
    }

    private QueryHistoryDto toHistoryDto(QueryHistoryEntity entity) {
        try {
            var citations = objectMapper.readValue(
                    entity.getCitationsJson(),
                    objectMapper.getTypeFactory()
                            .constructCollectionType(List.class, com.cortex.gateway.dto.query.CitationDto.class));
            @SuppressWarnings("unchecked")
            List<com.cortex.gateway.dto.query.CitationDto> typedCitations =
                    (List<com.cortex.gateway.dto.query.CitationDto>) citations;
            return new QueryHistoryDto(
                    entity.getId(),
                    entity.getCollectionId(),
                    entity.getQuestion(),
                    entity.getAnswer(),
                    entity.getMode(),
                    typedCitations,
                    entity.getCreatedAt());
        } catch (JsonProcessingException exception) {
            throw new IllegalStateException("Corrupt citations JSON for query history " + entity.getId(), exception);
        }
    }

    private String serializeCitations(AiQueryResponse aiResponse) {
        try {
            var citations = aiResponse.citations().stream()
                    .map(com.cortex.gateway.dto.query.CitationDto::from)
                    .toList();
            return objectMapper.writeValueAsString(citations);
        } catch (JsonProcessingException exception) {
            throw new IllegalStateException("Failed to serialize citations", exception);
        }
    }
}
