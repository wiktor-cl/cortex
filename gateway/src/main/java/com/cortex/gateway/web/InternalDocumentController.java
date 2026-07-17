package com.cortex.gateway.web;

import com.cortex.gateway.dto.document.DocumentStatusUpdateRequest;
import com.cortex.gateway.service.DocumentService;
import jakarta.validation.Valid;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** Callback endpoint the worker reports ingestion outcomes to; authenticated via
 * InternalApiKeyFilter/ROLE_INTERNAL rather than a user JWT (see SecurityConfig). */
@RestController
@RequestMapping("/internal/documents")
public class InternalDocumentController {

    private final DocumentService documentService;

    public InternalDocumentController(DocumentService documentService) {
        this.documentService = documentService;
    }

    @PatchMapping("/{id}/status")
    public ResponseEntity<Void> updateStatus(
            @PathVariable UUID id, @Valid @RequestBody DocumentStatusUpdateRequest request) {
        documentService.applyStatusUpdate(id, request);
        return ResponseEntity.noContent().build();
    }
}
