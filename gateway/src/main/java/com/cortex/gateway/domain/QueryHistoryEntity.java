package com.cortex.gateway.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "query_history")
public class QueryHistoryEntity {

    @Id
    private UUID id = UUID.randomUUID();

    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @Column(name = "collection_id")
    private UUID collectionId;

    @Column(nullable = false, columnDefinition = "text")
    private String question;

    @Column(nullable = false, columnDefinition = "text")
    private String answer;

    @Column(nullable = false)
    private String mode;

    // Stored as pre-serialized JSON (the gateway just passes ai-service's citation payload
    // through), not mapped field-by-field - the gateway never needs to query inside it, only
    // to redisplay it, so a typed Java structure here would add ceremony without benefit.
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "citations_json", nullable = false, columnDefinition = "jsonb")
    private String citationsJson;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected QueryHistoryEntity() {
        // JPA
    }

    public QueryHistoryEntity(
            UUID userId, UUID collectionId, String question, String answer, String mode, String citationsJson) {
        this.userId = userId;
        this.collectionId = collectionId;
        this.question = question;
        this.answer = answer;
        this.mode = mode;
        this.citationsJson = citationsJson;
    }

    public UUID getId() {
        return id;
    }

    public UUID getUserId() {
        return userId;
    }

    public UUID getCollectionId() {
        return collectionId;
    }

    public String getQuestion() {
        return question;
    }

    public String getAnswer() {
        return answer;
    }

    public String getMode() {
        return mode;
    }

    public String getCitationsJson() {
        return citationsJson;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
