package com.cortex.gateway.config;

import com.cortex.gateway.observability.CorrelationIdFilter;
import org.slf4j.MDC;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.ClientRequest;
import org.springframework.web.reactive.function.client.ExchangeFilterFunction;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Configuration
public class WebClientConfig {

    @Bean
    public WebClient aiServiceWebClient(@Value("${cortex.ai-service.base-url}") String baseUrl) {
        return WebClient.builder()
                .baseUrl(baseUrl)
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
