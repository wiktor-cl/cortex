package com.cortex.gateway.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import com.cortex.gateway.domain.DocumentCollection;
import com.cortex.gateway.dto.collection.CollectionDto;
import com.cortex.gateway.dto.collection.CreateCollectionRequest;
import com.cortex.gateway.exception.ResourceNotFoundException;
import com.cortex.gateway.repository.CollectionRepository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class CollectionServiceTest {

    @Mock
    private CollectionRepository collectionRepository;

    @InjectMocks
    private CollectionService collectionService;

    @Test
    void createSavesAndReturnsDto() {
        UUID ownerId = UUID.randomUUID();
        when(collectionRepository.save(any(DocumentCollection.class))).thenAnswer(invocation -> invocation.getArgument(0));

        CollectionDto dto = collectionService.create(ownerId, new CreateCollectionRequest("Manuals", "desc"));

        assertThat(dto.name()).isEqualTo("Manuals");
        assertThat(dto.ownerId()).isEqualTo(ownerId);
    }

    @Test
    void listAllMapsEveryEntity() {
        DocumentCollection collection = new DocumentCollection("Manuals", "desc", UUID.randomUUID());
        when(collectionRepository.findAll()).thenReturn(List.of(collection));

        List<CollectionDto> result = collectionService.listAll();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).name()).isEqualTo("Manuals");
    }

    @Test
    void getByIdThrowsWhenMissing() {
        UUID id = UUID.randomUUID();
        when(collectionRepository.findById(id)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> collectionService.getById(id)).isInstanceOf(ResourceNotFoundException.class);
    }
}
