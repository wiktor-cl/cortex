package com.cortex.gateway.service;

import com.cortex.gateway.domain.Role;
import com.cortex.gateway.domain.User;
import com.cortex.gateway.dto.auth.AuthResponse;
import com.cortex.gateway.dto.auth.LoginRequest;
import com.cortex.gateway.dto.auth.RegisterRequest;
import com.cortex.gateway.exception.DuplicateEmailException;
import com.cortex.gateway.exception.InvalidCredentialsException;
import com.cortex.gateway.repository.UserRepository;
import com.cortex.gateway.security.JwtService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new DuplicateEmailException(request.email());
        }
        User user = new User(request.email(), passwordEncoder.encode(request.password()), Role.USER);
        userRepository.save(user);
        return issueToken(user);
    }

    public AuthResponse login(LoginRequest request) {
        User user = userRepository
                .findByEmail(request.email())
                .orElseThrow(InvalidCredentialsException::new);
        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new InvalidCredentialsException();
        }
        return issueToken(user);
    }

    private AuthResponse issueToken(User user) {
        String token = jwtService.generateToken(user.getId(), user.getEmail(), user.getRole());
        return new AuthResponse(token, user.getId(), user.getEmail(), user.getRole());
    }
}
