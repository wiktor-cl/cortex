package com.cortex.gateway.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

/**
 * The gateway's own record of an uploaded document - user-facing metadata (who uploaded it, which
 * collection, its processing status) as seen by the frontend. This is a deliberately different
 * table from the RAG engine's own "documents" table in ai-service's "rag" Postgres schema, which
 * tracks chunk/embedding state instead. The two are linked only by sharing the same id (set here at
 * upload time and passed through to ai-service) - not by a physical foreign key, since the two
 * services own their schemas independently. See ARCHITECTURE.md.
 */
@Entity
@Table(name = "documents")
public class DocumentEntity {

    @Id
    private UUID id = UUID.randomUUID();

    @Column(name = "collection_id", nullable = false)
    private UUID collectionId;

    @Column(nullable = false)
    private String filename;

    @Column(name = "uploaded_by", nullable = false)
    private UUID uploadedBy;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private DocumentStatus status = DocumentStatus.QUEUED;

    @Column(name = "chunk_count", nullable = false)
    private int chunkCount = 0;

    @Column(name = "error_message")
    private String errorMessage;

    @Column(name = "uploaded_at", nullable = false)
    private Instant uploadedAt = Instant.now();

    protected DocumentEntity() {
        // JPA
    }

    public DocumentEntity(UUID id, UUID collectionId, String filename, UUID uploadedBy) {
        this.id = id;
        this.collectionId = collectionId;
        this.filename = filename;
        this.uploadedBy = uploadedBy;
    }

    public UUID getId() {
        return id;
    }

    public UUID getCollectionId() {
        return collectionId;
    }

    public String getFilename() {
        return filename;
    }

    public UUID getUploadedBy() {
        return uploadedBy;
    }

    public DocumentStatus getStatus() {
        return status;
    }

    public int getChunkCount() {
        return chunkCount;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public Instant getUploadedAt() {
        return uploadedAt;
    }

    public void applyStatusUpdate(DocumentStatus status, int chunkCount, String errorMessage) {
        this.status = status;
        this.chunkCount = chunkCount;
        this.errorMessage = errorMessage;
    }
}
