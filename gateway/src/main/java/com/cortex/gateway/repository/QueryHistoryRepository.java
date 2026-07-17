package com.cortex.gateway.repository;

import com.cortex.gateway.domain.QueryHistoryEntity;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface QueryHistoryRepository extends JpaRepository<QueryHistoryEntity, UUID> {
    List<QueryHistoryEntity> findByUserIdOrderByCreatedAtDesc(UUID userId);
}
