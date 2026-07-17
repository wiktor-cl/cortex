package com.cortex.gateway.web;

import com.cortex.gateway.dto.document.DocumentDto;
import com.cortex.gateway.security.CortexPrincipal;
import com.cortex.gateway.service.DocumentService;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
public class DocumentController {

    private final DocumentService documentService;

    public DocumentController(DocumentService documentService) {
        this.documentService = documentService;
    }

    @PostMapping("/api/collections/{collectionId}/documents")
    public ResponseEntity<DocumentDto> upload(
            @AuthenticationPrincipal CortexPrincipal principal,
            @PathVariable UUID collectionId,
            @RequestParam("file") MultipartFile file) {
        DocumentDto uploaded = documentService.upload(collectionId, principal.userId(), file);
        return ResponseEntity.status(HttpStatus.CREATED).body(uploaded);
    }

    @GetMapping("/api/collections/{collectionId}/documents")
    public List<DocumentDto> listByCollection(@PathVariable UUID collectionId) {
        return documentService.listByCollection(collectionId);
    }

    @GetMapping("/api/documents/{id}")
    public DocumentDto getById(@PathVariable UUID id) {
        return documentService.getById(id);
    }

    @DeleteMapping("/api/documents/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        documentService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
