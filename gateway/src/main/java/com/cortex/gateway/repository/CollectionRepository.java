package com.cortex.gateway.repository;

import com.cortex.gateway.domain.DocumentCollection;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CollectionRepository extends JpaRepository<DocumentCollection, UUID> {}
