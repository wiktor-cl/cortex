package com.cortex.gateway.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.when;

import com.cortex.gateway.domain.DocumentEntity;
import com.cortex.gateway.domain.DocumentStatus;
import com.cortex.gateway.domain.Role;
import com.cortex.gateway.domain.User;
import com.cortex.gateway.dto.admin.AdminStatsDto;
import com.cortex.gateway.dto.admin.UserDto;
import com.cortex.gateway.exception.ResourceNotFoundException;
import com.cortex.gateway.repository.CollectionRepository;
import com.cortex.gateway.repository.DocumentRepository;
import com.cortex.gateway.repository.QueryHistoryRepository;
import com.cortex.gateway.repository.UserRepository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class AdminServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private CollectionRepository collectionRepository;

    @Mock
    private DocumentRepository documentRepository;

    @Mock
    private QueryHistoryRepository queryHistoryRepository;

    @InjectMocks
    private AdminService adminService;

    @Test
    void statsAggregatesCountsAndFillsMissingStatuses() {
        DocumentEntity done = new DocumentEntity(UUID.randomUUID(), UUID.randomUUID(), "a.pdf", UUID.randomUUID());
        done.applyStatusUpdate(DocumentStatus.DONE, 3, null);
        when(documentRepository.findAll()).thenReturn(List.of(done));
        when(userRepository.count()).thenReturn(2L);
        when(collectionRepository.count()).thenReturn(1L);
        when(queryHistoryRepository.count()).thenReturn(5L);

        AdminStatsDto stats = adminService.stats();

        assertThat(stats.userCount()).isEqualTo(2L);
        assertThat(stats.documentCount()).isEqualTo(1L);
        assertThat(stats.documentsByStatus().get("DONE")).isEqualTo(1L);
        assertThat(stats.documentsByStatus().get("QUEUED")).isEqualTo(0L);
        assertThat(stats.documentsByStatus().get("FAILED")).isEqualTo(0L);
    }

    @Test
    void updateRoleChangesRoleOfExistingUser() {
        User user = new User("alice@example.com", "hashed", Role.USER);
        when(userRepository.findById(user.getId())).thenReturn(Optional.of(user));

        UserDto result = adminService.updateRole(user.getId(), Role.ADMIN);

        assertThat(result.role()).isEqualTo(Role.ADMIN);
    }

    @Test
    void updateRoleThrowsWhenUserMissing() {
        UUID id = UUID.randomUUID();
        when(userRepository.findById(id)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> adminService.updateRole(id, Role.ADMIN))
                .isInstanceOf(ResourceNotFoundException.class);
    }
}
