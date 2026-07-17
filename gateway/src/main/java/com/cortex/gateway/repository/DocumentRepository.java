package com.cortex.gateway.repository;

import com.cortex.gateway.domain.DocumentEntity;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DocumentRepository extends JpaRepository<DocumentEntity, UUID> {
    List<DocumentEntity> findByCollectionId(UUID collectionId);
}
