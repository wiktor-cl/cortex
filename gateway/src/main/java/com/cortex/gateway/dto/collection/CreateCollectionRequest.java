package com.cortex.gateway.dto.collection;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateCollectionRequest(
        @NotBlank @Size(max = 200) String name, @Size(max = 2000) String description) {}
