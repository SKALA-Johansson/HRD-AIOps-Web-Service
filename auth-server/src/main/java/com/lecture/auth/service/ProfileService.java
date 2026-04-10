package com.lecture.auth.service;

import com.lecture.auth.dto.OnboardingEvent;
import com.lecture.auth.dto.ProfileRequest;
import com.lecture.auth.model.Profile;
import com.lecture.auth.model.User;
import com.lecture.auth.repository.ProfileRepository;
import com.lecture.auth.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;

@Service
@Slf4j
@RequiredArgsConstructor
public class ProfileService {

    private final ProfileRepository profileRepository;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    private static final String TOPIC_ONBOARDING_EVENTS = "onboarding-events";

    @Transactional
    public Profile registerEmployee(String name, String username, String department, String birthDate, MultipartFile file) {
        // 1. User 계정 생성 (이미 존재하는 경우 예외 처리 생략하거나 조회)
        User user = userRepository.findByUsername(username)
                .orElseGet(() -> {
                    User newUser = User.builder()
                            .username(username)
                            .password(passwordEncoder.encode(birthDate))
                            .name(name)
                            .role(User.Role.EMPLOYEE)
                            .build();
                    return userRepository.save(newUser);
                });

        // 2. Profile 생성 또는 업데이트
        Profile profile = profileRepository.findByUser(user)
                .orElseGet(() -> Profile.builder().user(user).build());

        profile.setDepartment(department);
        Profile savedProfile = profileRepository.save(profile);

        // 3. Kafka Event 발행: User.ProfileUpdated
        String dummyPdfUrl = "http://dummy-storage.local/resumes/" + username + ".pdf";

        OnboardingEvent event = OnboardingEvent.builder()
                .eventType("User.ProfileUpdated")
                .userId(user.getUserId())
                .username(user.getUsername())
                .name(user.getName())
                .department(department)
                .pdfUrl(dummyPdfUrl)
                .occurredAt(LocalDateTime.now())
                .build();

        log.info("Publishing onboarding event: {}", event);
        kafkaTemplate.send(TOPIC_ONBOARDING_EVENTS, event);

        return savedProfile;
    }

    @Transactional(readOnly = true)
    public Profile getProfileByUsername(String username) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found"));
        return profileRepository.findByUser(user)
                .orElseThrow(() -> new RuntimeException("Profile not found"));
    }

    @Transactional
    public Profile updateProfileByUsername(String username, ProfileRequest request) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found"));
        Profile profile = profileRepository.findByUser(user)
                .orElseThrow(() -> new RuntimeException("Profile not found"));

        profile.setDesiredCompany(request.getDesiredCompany());
        profile.setDesiredJob(request.getDesiredJob());
        profile.setCareerHistory(request.getCareerHistory());
        profile.setSelfIntroduction(request.getSelfIntroduction());
        profile.setPreAssessment(request.getPreAssessment());

        return profileRepository.save(profile);
    }

    @Transactional
    public void createProfileForUser(User user) {
        Profile profile = Profile.builder()
                .user(user)
                .build();
        profileRepository.save(profile);
    }
}
