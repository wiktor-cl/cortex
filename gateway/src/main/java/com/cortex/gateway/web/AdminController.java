package com.cortex.gateway.web;

import com.cortex.gateway.dto.admin.AdminStatsDto;
import com.cortex.gateway.dto.admin.UpdateUserRoleRequest;
import com.cortex.gateway.dto.admin.UserDto;
import com.cortex.gateway.service.AdminService;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin")
public class AdminController {

    private final AdminService adminService;

    public AdminController(AdminService adminService) {
        this.adminService = adminService;
    }

    @GetMapping("/stats")
    public AdminStatsDto stats() {
        return adminService.stats();
    }

    @GetMapping("/users")
    public List<UserDto> listUsers() {
        return adminService.listUsers();
    }

    @PatchMapping("/users/{id}/role")
    public UserDto updateRole(@PathVariable UUID id, @Valid @RequestBody UpdateUserRoleRequest request) {
        return adminService.updateRole(id, request.role());
    }
}
