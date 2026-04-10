package com.lecture.auth.service;

import com.lecture.auth.dto.AuthResponse;
import com.lecture.auth.dto.LoginRequest;
import com.lecture.auth.dto.SignupRequest;
import com.lecture.auth.model.User;
import com.lecture.auth.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jwt.JwtClaimsSet;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtEncoderParameters;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.time.temporal.ChronoUnit;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final ProfileService profileService;
    private final PasswordEncoder passwordEncoder;
    private final JwtEncoder jwtEncoder;

    @Transactional
    public User signup(SignupRequest request) {
        if (userRepository.findByUsername(request.getUsername()).isPresent()) {
            throw new RuntimeException("Username (Employee ID) already exists");
        }

        User user = User.builder()
                .username(request.getUsername())
                .password(passwordEncoder.encode(request.getPassword()))
                .name(request.getName())
                .role(request.getRole() != null ? request.getRole() : User.Role.EMPLOYEE)
                .build();

        User savedUser = userRepository.save(user);
        profileService.createProfileForUser(savedUser);

        return savedUser;
    }

    @Transactional(readOnly = true)
    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new RuntimeException("User not found"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("Invalid password");
        }

        String accessToken = generateToken(user, 1); // 1 hour
        String refreshToken = generateToken(user, 24 * 7); // 7 days

        return AuthResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .user(AuthResponse.UserInfo.builder()
                        .userId(user.getUserId())
                        .name(user.getName())
                        .role(user.getRole())
                        .build())
                .build();
    }

    private String generateToken(User user, long hours) {
        Instant now = Instant.now();
        JwtClaimsSet claims = JwtClaimsSet.builder()
                .issuer("http://localhost:8080")
                .issuedAt(now)
                .expiresAt(now.plus(hours, ChronoUnit.HOURS))
                .subject(user.getUserId())
                .claim("user_id", user.getUserId())
                .claim("username", user.getUsername())
                .claim("role", user.getRole().name())
                .claim("name", user.getName())
                .build();

        return jwtEncoder.encode(JwtEncoderParameters.from(claims)).getTokenValue();
    }
}
