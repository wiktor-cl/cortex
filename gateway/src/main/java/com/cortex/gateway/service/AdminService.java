package com.cortex.gateway.service;

import com.cortex.gateway.domain.DocumentEntity;
import com.cortex.gateway.domain.DocumentStatus;
import com.cortex.gateway.domain.User;
import com.cortex.gateway.dto.admin.AdminStatsDto;
import com.cortex.gateway.dto.admin.UserDto;
import com.cortex.gateway.exception.ResourceNotFoundException;
import com.cortex.gateway.repository.CollectionRepository;
import com.cortex.gateway.repository.DocumentRepository;
import com.cortex.gateway.repository.QueryHistoryRepository;
import com.cortex.gateway.repository.UserRepository;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AdminService {

    private final UserRepository userRepository;
    private final CollectionRepository collectionRepository;
    private final DocumentRepository documentRepository;
    private final QueryHistoryRepository queryHistoryRepository;

    public AdminService(
            UserRepository userRepository,
            CollectionRepository collectionRepository,
            DocumentRepository documentRepository,
            QueryHistoryRepository queryHistoryRepository) {
        this.userRepository = userRepository;
        this.collectionRepository = collectionRepository;
        this.documentRepository = documentRepository;
        this.queryHistoryRepository = queryHistoryRepository;
    }

    public AdminStatsDto stats() {
        List<DocumentEntity> documents = documentRepository.findAll();
        Map<String, Long> byStatus = documents.stream()
                .collect(Collectors.groupingBy(document -> document.getStatus().name(), Collectors.counting()));
        for (DocumentStatus status : DocumentStatus.values()) {
            byStatus.putIfAbsent(status.name(), 0L);
        }
        return new AdminStatsDto(
                userRepository.count(),
                collectionRepository.count(),
                documents.size(),
                queryHistoryRepository.count(),
                byStatus);
    }

    public List<UserDto> listUsers() {
        return userRepository.findAll().stream().map(UserDto::from).toList();
    }

    @Transactional
    public UserDto updateRole(UUID userId, com.cortex.gateway.domain.Role role) {
        User user = userRepository
                .findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User '" + userId + "' not found"));
        user.setRole(role);
        return UserDto.from(user);
    }
}
