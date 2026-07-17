package com.cortex.gateway.web;

import com.cortex.gateway.dto.collection.CollectionDto;
import com.cortex.gateway.dto.collection.CreateCollectionRequest;
import com.cortex.gateway.security.CortexPrincipal;
import com.cortex.gateway.service.CollectionService;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/collections")
public class CollectionController {

    private final CollectionService collectionService;

    public CollectionController(CollectionService collectionService) {
        this.collectionService = collectionService;
    }

    @PostMapping
    public ResponseEntity<CollectionDto> create(
            @AuthenticationPrincipal CortexPrincipal principal, @Valid @RequestBody CreateCollectionRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(collectionService.create(principal.userId(), request));
    }

    @GetMapping
    public List<CollectionDto> listAll() {
        return collectionService.listAll();
    }

    @GetMapping("/{id}")
    public CollectionDto getById(@PathVariable UUID id) {
        return collectionService.getById(id);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        collectionService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
