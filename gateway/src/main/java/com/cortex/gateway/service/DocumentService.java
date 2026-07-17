package com.cortex.gateway.service;

import com.cortex.gateway.domain.DocumentEntity;
import com.cortex.gateway.domain.DocumentStatus;
import com.cortex.gateway.dto.document.DocumentDto;
import com.cortex.gateway.dto.document.DocumentStatusUpdateRequest;
import com.cortex.gateway.exception.ResourceNotFoundException;
import com.cortex.gateway.repository.DocumentRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.slf4j.MDC;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

/**
 * Owns the gateway side of document upload: writes the binary and a JSON "sidecar" file to a
 * directory shared with the worker container (see docker-compose.yml). The sidecar is written
 * strictly after the binary, since its appearance is what the worker's folder watcher treats as
 * the "upload is complete, safe to enqueue" signal - writing it first would let the watcher pick
 * up a half-written file. See worker/worker/watcher.py for the consuming side of this contract.
 */
@Service
public class DocumentService {

    private final DocumentRepository documentRepository;
    private final ObjectMapper objectMapper;
    private final Path uploadsDir;

    public DocumentService(
            DocumentRepository documentRepository,
            ObjectMapper objectMapper,
            @Value("${cortex.uploads.dir}") String uploadsDir) {
        this.documentRepository = documentRepository;
        this.objectMapper = objectMapper;
        this.uploadsDir = Path.of(uploadsDir);
    }

    public DocumentDto upload(UUID collectionId, UUID uploadedBy, MultipartFile file) {
        String filename = file.getOriginalFilename() != null ? file.getOriginalFilename() : "unknown";
        DocumentEntity entity = new DocumentEntity(UUID.randomUUID(), collectionId, filename, uploadedBy);
        documentRepository.save(entity);
        writeToSharedVolume(entity, file);
        return DocumentDto.from(entity);
    }

    private void writeToSharedVolume(DocumentEntity entity, MultipartFile file) {
        try {
            Files.createDirectories(uploadsDir);
            Path binaryPath = uploadsDir.resolve(entity.getId() + "__" + entity.getFilename());
            file.transferTo(binaryPath);

            Map<String, String> sidecar = new HashMap<>();
            sidecar.put("documentId", entity.getId().toString());
            sidecar.put("collectionId", entity.getCollectionId().toString());
            sidecar.put("filename", entity.getFilename());
            String correlationId = MDC.get("correlationId");
            if (correlationId != null) {
                sidecar.put("correlationId", correlationId);
            }
            Path sidecarPath = uploadsDir.resolve(entity.getId() + ".json");
            Files.write(sidecarPath, objectMapper.writeValueAsBytes(sidecar));
        } catch (IOException exception) {
            throw new UncheckedIOException("Failed to write uploaded document to shared volume", exception);
        }
    }

    public List<DocumentDto> listByCollection(UUID collectionId) {
        return documentRepository.findByCollectionId(collectionId).stream().map(DocumentDto::from).toList();
    }

    public DocumentDto getById(UUID id) {
        return DocumentDto.from(findEntity(id));
    }

    public void delete(UUID id) {
        documentRepository.delete(findEntity(id));
    }

    @Transactional
    public void applyStatusUpdate(UUID id, DocumentStatusUpdateRequest request) {
        DocumentEntity entity = findEntity(id);
        entity.applyStatusUpdate(request.status(), request.chunkCount(), request.errorMessage());
    }

    private DocumentEntity findEntity(UUID id) {
        return documentRepository
                .findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Document '" + id + "' not found"));
    }
}
