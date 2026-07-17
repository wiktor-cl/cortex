package com.cortex.gateway.config;

import com.cortex.gateway.observability.CorrelationIdFilter;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.MDC;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.MediaType;
import org.springframework.http.codec.json.Jackson2JsonDecoder;
import org.springframework.http.codec.json.Jackson2JsonEncoder;
import org.springframework.web.reactive.function.client.ClientRequest;
import org.springframework.web.reactive.function.client.ExchangeFilterFunction;
import org.springframework.web.reactive.function.client.ExchangeStrategies;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Configuration
public class WebClientConfig {

    /**
     * Spring Boot 4's auto-configured {@code WebClient.Builder} wires Jackson 3 codecs by
     * default, which silently ignore the classic {@code com.fasterxml.jackson} {@code @JsonNaming}
     * annotations on the ai/* DTOs (they only recognize the {@code tools.jackson} equivalent) -
     * fields come back null instead of snake_case-mapped. Explicit classic Jackson2 codecs, backed
     * by the same {@link ObjectMapper} bean used everywhere else, sidestep that mismatch.
     */
    @Bean
    public WebClient aiServiceWebClient(
            @Value("${cortex.ai-service.base-url}") String baseUrl, ObjectMapper objectMapper) {
        ExchangeStrategies strategies = ExchangeStrategies.builder()
                .codecs(configurer -> {
                    configurer.defaultCodecs().jackson2JsonEncoder(new Jackson2JsonEncoder(objectMapper, MediaType.APPLICATION_JSON));
                    configurer.defaultCodecs().jackson2JsonDecoder(new Jackson2JsonDecoder(objectMapper, MediaType.APPLICATION_JSON));
                })
                .build();
        return WebClient.builder()
                .baseUrl(baseUrl)
                .exchangeStrategies(strategies)
                .filter(propagateCorrelationId())
                .build();
    }

    /** Forwards the current request's correlation id (bound to MDC by CorrelationIdFilter) onto
     * every outgoing call to ai-service, extending the trace across the service boundary. */
    private ExchangeFilterFunction propagateCorrelationId() {
        return ExchangeFilterFunction.ofRequestProcessor(request -> {
            String correlationId = MDC.get(CorrelationIdFilter.MDC_KEY);
            if (correlationId == null) {
                return Mono.just(request);
            }
            return Mono.just(ClientRequest.from(request)
                    .header(CorrelationIdFilter.HEADER_NAME, correlationId)
                    .build());
        });
    }
}
