package com.cortex.gateway.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Spring Boot 4 defaults its Jackson autoconfiguration to Jackson 3 (the {@code tools.jackson}
 * package) and no longer auto-registers a classic {@code com.fasterxml.jackson.databind.ObjectMapper}
 * bean. This gateway's DTOs (via {@code @JsonNaming}), jjwt-jackson, and springdoc-openapi all still
 * target classic Jackson 2, so the bean is defined explicitly here rather than migrating the whole
 * codebase to the new package - the same kind of deliberate, documented version-drift call as the
 * Spring Boot 4.1.0 substitution itself.
 */
@Configuration
public class JacksonConfig {

    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper().registerModule(new JavaTimeModule());
    }
}
