package com.cortex.gateway.service;

import com.cortex.gateway.domain.DocumentCollection;
import com.cortex.gateway.dto.collection.CollectionDto;
import com.cortex.gateway.dto.collection.CreateCollectionRequest;
import com.cortex.gateway.exception.ResourceNotFoundException;
import com.cortex.gateway.repository.CollectionRepository;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class CollectionService {

    private final CollectionRepository collectionRepository;

    public CollectionService(CollectionRepository collectionRepository) {
        this.collectionRepository = collectionRepository;
    }

    public CollectionDto create(UUID ownerId, CreateCollectionRequest request) {
        DocumentCollection collection =
                new DocumentCollection(request.name(), request.description(), ownerId);
        return CollectionDto.from(collectionRepository.save(collection));
    }

    public List<CollectionDto> listAll() {
        return collectionRepository.findAll().stream().map(CollectionDto::from).toList();
    }

    public CollectionDto getById(UUID id) {
        return CollectionDto.from(findEntity(id));
    }

    public void delete(UUID id) {
        collectionRepository.delete(findEntity(id));
    }

    private DocumentCollection findEntity(UUID id) {
        return collectionRepository
                .findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Collection '" + id + "' not found"));
    }
}
