package com.cortex.gateway.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.cortex.gateway.domain.Role;
import com.cortex.gateway.domain.User;
import com.cortex.gateway.dto.auth.AuthResponse;
import com.cortex.gateway.dto.auth.LoginRequest;
import com.cortex.gateway.dto.auth.RegisterRequest;
import com.cortex.gateway.exception.DuplicateEmailException;
import com.cortex.gateway.exception.InvalidCredentialsException;
import com.cortex.gateway.repository.UserRepository;
import com.cortex.gateway.security.JwtService;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtService jwtService;

    private AuthService authService;

    private AuthService service() {
        return new AuthService(userRepository, passwordEncoder, jwtService);
    }

    @Test
    void registerCreatesUserAndReturnsToken() {
        authService = service();
        RegisterRequest request = new RegisterRequest("alice@example.com", "password123");
        when(userRepository.existsByEmail("alice@example.com")).thenReturn(false);
        when(passwordEncoder.encode("password123")).thenReturn("hashed");
        when(jwtService.generateToken(any(), any(), any())).thenReturn("jwt-token");

        AuthResponse response = authService.register(request);

        assertThat(response.token()).isEqualTo("jwt-token");
        assertThat(response.email()).isEqualTo("alice@example.com");
        assertThat(response.role()).isEqualTo(Role.USER);
        verify(userRepository).save(any(User.class));
    }

    @Test
    void registerRejectsDuplicateEmail() {
        authService = service();
        when(userRepository.existsByEmail("alice@example.com")).thenReturn(true);

        assertThatThrownBy(() -> authService.register(new RegisterRequest("alice@example.com", "password123")))
                .isInstanceOf(DuplicateEmailException.class);
    }

    @Test
    void loginSucceedsWithCorrectPassword() {
        authService = service();
        User user = new User("alice@example.com", "hashed", Role.USER);
        when(userRepository.findByEmail("alice@example.com")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("password123", "hashed")).thenReturn(true);
        when(jwtService.generateToken(any(), any(), any())).thenReturn("jwt-token");

        AuthResponse response = authService.login(new LoginRequest("alice@example.com", "password123"));

        assertThat(response.token()).isEqualTo("jwt-token");
    }

    @Test
    void loginRejectsUnknownEmail() {
        authService = service();
        when(userRepository.findByEmail("nobody@example.com")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> authService.login(new LoginRequest("nobody@example.com", "password123")))
                .isInstanceOf(InvalidCredentialsException.class);
    }

    @Test
    void loginRejectsWrongPassword() {
        authService = service();
        User user = new User("alice@example.com", "hashed", Role.USER);
        when(userRepository.findByEmail("alice@example.com")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("wrong", "hashed")).thenReturn(false);

        assertThatThrownBy(() -> authService.login(new LoginRequest("alice@example.com", "wrong")))
                .isInstanceOf(InvalidCredentialsException.class);
    }
}
