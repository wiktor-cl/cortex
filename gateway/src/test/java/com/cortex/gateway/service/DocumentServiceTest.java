package com.cortex.gateway.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import com.cortex.gateway.domain.DocumentEntity;
import com.cortex.gateway.domain.DocumentStatus;
import com.cortex.gateway.dto.document.DocumentDto;
import com.cortex.gateway.dto.document.DocumentStatusUpdateRequest;
import com.cortex.gateway.exception.ResourceNotFoundException;
import com.cortex.gateway.repository.DocumentRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.api.io.TempDir;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockMultipartFile;

@ExtendWith(MockitoExtension.class)
class DocumentServiceTest {

    @Mock
    private DocumentRepository documentRepository;

    @TempDir
    Path tempDir;

    private DocumentService service() {
        return new DocumentService(documentRepository, new ObjectMapper(), tempDir.toString());
    }

    @Test
    void uploadWritesBinaryAndSidecarToSharedVolume() throws Exception {
        DocumentService service = service();
        UUID collectionId = UUID.randomUUID();
        UUID uploadedBy = UUID.randomUUID();
        MockMultipartFile file =
                new MockMultipartFile("file", "manual.pdf", "application/pdf", "content".getBytes());

        DocumentDto dto = service.upload(collectionId, uploadedBy, file);

        Path binaryPath = tempDir.resolve(dto.id() + "__manual.pdf");
        Path sidecarPath = tempDir.resolve(dto.id() + ".json");
        assertThat(Files.exists(binaryPath)).isTrue();
        assertThat(Files.exists(sidecarPath)).isTrue();
        assertThat(Files.readString(sidecarPath)).contains(dto.id().toString(), collectionId.toString(), "manual.pdf");
        assertThat(Files.readAllBytes(binaryPath)).isEqualTo("content".getBytes());
    }

    @Test
    void applyStatusUpdateMutatesTrackedEntity() {
        DocumentService service = service();
        DocumentEntity entity =
                new DocumentEntity(UUID.randomUUID(), UUID.randomUUID(), "manual.pdf", UUID.randomUUID());
        when(documentRepository.findById(entity.getId())).thenReturn(Optional.of(entity));

        service.applyStatusUpdate(entity.getId(), new DocumentStatusUpdateRequest(DocumentStatus.DONE, 7, null));

        assertThat(entity.getStatus()).isEqualTo(DocumentStatus.DONE);
        assertThat(entity.getChunkCount()).isEqualTo(7);
    }

    @Test
    void applyStatusUpdateThrowsWhenDocumentMissing() {
        DocumentService service = service();
        UUID id = UUID.randomUUID();
        when(documentRepository.findById(id)).thenReturn(Optional.empty());

        assertThatThrownBy(() ->
                        service.applyStatusUpdate(id, new DocumentStatusUpdateRequest(DocumentStatus.FAILED, 0, "boom")))
                .isInstanceOf(ResourceNotFoundException.class);
    }
}
