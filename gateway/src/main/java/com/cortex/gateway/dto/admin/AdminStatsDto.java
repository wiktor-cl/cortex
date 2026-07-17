package com.cortex.gateway.dto.admin;

import java.util.Map;

public record AdminStatsDto(
        long userCount,
        long collectionCount,
        long documentCount,
        long queryCount,
        Map<String, Long> documentsByStatus) {}
