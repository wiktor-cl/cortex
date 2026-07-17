package com.cortex.gateway.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import com.cortex.gateway.domain.QueryHistoryEntity;
import com.cortex.gateway.dto.query.QueryRequestDto;
import com.cortex.gateway.dto.query.QueryResponseDto;
import com.cortex.gateway.dto.query.ai.AiCitation;
import com.cortex.gateway.dto.query.ai.AiQueryResponse;
import com.cortex.gateway.exception.AiServiceException;
import com.cortex.gateway.repository.QueryHistoryRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Answers;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;

@ExtendWith(MockitoExtension.class)
class QueryServiceTest {

    @Mock(answer = Answers.RETURNS_DEEP_STUBS)
    private WebClient webClient;

    @Mock
    private QueryHistoryRepository queryHistoryRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    private QueryService service() {
        return new QueryService(webClient, queryHistoryRepository, objectMapper);
    }

    @Test
    void askCallsAiServiceAndPersistsHistory() {
        AiCitation citation =
                new AiCitation(UUID.randomUUID(), "manual.pdf", 3, 0, "snippet text", 0.87);
        AiQueryResponse aiResponse =
                new AiQueryResponse("The answer is 42.", "extractive", List.of(citation), List.of());
        when(webClient.post().uri("/query").bodyValue(any()).retrieve().bodyToMono(AiQueryResponse.class))
                .thenReturn(Mono.just(aiResponse));

        UUID userId = UUID.randomUUID();
        QueryResponseDto response = service().ask(userId, new QueryRequestDto("How do I reset it?", null, 5));

        assertThat(response.answer()).isEqualTo("The answer is 42.");
        assertThat(response.mode()).isEqualTo("extractive");
        assertThat(response.citations()).hasSize(1);

        ArgumentCaptor<QueryHistoryEntity> captor = ArgumentCaptor.forClass(QueryHistoryEntity.class);
        org.mockito.Mockito.verify(queryHistoryRepository).save(captor.capture());
        assertThat(captor.getValue().getUserId()).isEqualTo(userId);
        assertThat(captor.getValue().getCitationsJson()).contains("manual.pdf");
    }

    @Test
    void askWrapsWebClientFailureAsAiServiceException() {
        when(webClient.post().uri("/query").bodyValue(any()).retrieve().bodyToMono(AiQueryResponse.class))
                .thenReturn(Mono.error(WebClientResponseException.create(
                        502, "Bad Gateway", null, new byte[0], null)));

        assertThatThrownBy(() -> service().ask(UUID.randomUUID(), new QueryRequestDto("question?", null, 5)))
                .isInstanceOf(AiServiceException.class);
    }
}
