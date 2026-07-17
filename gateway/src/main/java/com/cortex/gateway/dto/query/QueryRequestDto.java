package com.cortex.gateway.dto.query;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.UUID;

public record QueryRequestDto(
        @NotBlank @Size(max = 2000) String question, UUID collectionId, @Min(1) @Max(20) Integer topK) {}
