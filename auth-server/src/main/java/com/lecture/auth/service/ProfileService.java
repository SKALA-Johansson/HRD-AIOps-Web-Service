package com.lecture.auth.service;

import com.lecture.auth.dto.ProfileRequest;
import com.lecture.auth.model.Profile;
import com.lecture.auth.model.User;
import com.lecture.auth.repository.ProfileRepository;
import com.lecture.auth.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class ProfileService {

    private final ProfileRepository profileRepository;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final RestTemplate restTemplate = new RestTemplate();

    private static final String TOPIC_ONBOARDING_EVENTS = "onboarding-events";

    @Value("${external.curriculum-designer-url:http://curriculum-designer-agent:10022}")
    private String curriculumDesignerUrl;

    @Transactional
    public Map<String, Object> registerEmployee(String name, String username, String department, String birthDate, MultipartFile file) {
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

        // 3. 업로드한 PDF 기반으로 커리큘럼 생성 트리거 (부서 정석 커리큘럼 + 보유 역량 제외)
        String curriculumId = triggerCurriculumGeneration(file, name, username, department, birthDate);

        // 3. Kafka Event 발행: User.ProfileUpdated (event_type envelope)
        String dummyPdfUrl = "http://dummy-storage.local/resumes/" + username + ".pdf";

        Map<String, Object> payload = new HashMap<>();
        payload.put("user_id", user.getUserId());
        payload.put("username", user.getUsername());
        payload.put("employee_id", user.getUsername());
        payload.put("employee_name", user.getName());
        payload.put("department", department);
        payload.put("role", "신입");
        payload.put("career_level", "junior");
        payload.put("experience_years", 0);
        payload.put("skills", List.of());
        payload.put("pdf_url", dummyPdfUrl);

        Map<String, Object> event = new HashMap<>();
        event.put("event_type", "User.ProfileUpdated");
        event.put("event_id", user.getUserId());
        event.put("timestamp", LocalDateTime.now().toString());
        event.put("source", "auth-server");
        event.put("payload", payload);

        log.info("Publishing onboarding event: {}", event);
        kafkaTemplate.send(TOPIC_ONBOARDING_EVENTS, event);

        Map<String, Object> result = new HashMap<>();
        result.put("profileId", savedProfile.getProfileId());
        result.put("userId", user.getUserId());
        result.put("username", user.getUsername());
        result.put("department", savedProfile.getDepartment());
        result.put("curriculumId", curriculumId);
        result.put("curriculumRequested", curriculumId != null);
        return result;
    }

    private String triggerCurriculumGeneration(
            MultipartFile file,
            String name,
            String username,
            String department,
            String birthDate
    ) {
        if (file == null || file.isEmpty()) {
            log.warn("[Curriculum] PDF 파일이 없어 생성 요청을 건너뜁니다. username={}", username);
            return null;
        }

        String endpoint = curriculumDesignerUrl + "/curriculums/generate-from-pdf";

        try {
            byte[] bytes = file.getBytes();
            String filename = (file.getOriginalFilename() == null || file.getOriginalFilename().isBlank())
                    ? username + ".pdf"
                    : file.getOriginalFilename();

            ByteArrayResource resource = new ByteArrayResource(bytes) {
                @Override
                public String getFilename() {
                    return filename;
                }
            };

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", resource);
            body.add("name", name);
            body.add("employeeNo", username);
            body.add("birthDate6", birthDate);
            body.add("department", department);
            body.add("title", name + " 맞춤형 커리큘럼");

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);
            HttpEntity<MultiValueMap<String, Object>> request = new HttpEntity<>(body, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(endpoint, request, Map.class);
            if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
                log.error("[Curriculum] 생성 요청 실패: status={}", response.getStatusCode());
                return null;
            }

            Object dataObj = response.getBody().get("data");
            if (dataObj instanceof Map<?, ?> dataMap) {
                Object curriculumId = dataMap.get("curriculumId");
                if (curriculumId != null) {
                    String id = curriculumId.toString();
                    log.info("[Curriculum] 생성 요청 성공: curriculumId={}, username={}", id, username);
                    return id;
                }
            }
            log.warn("[Curriculum] 응답에 curriculumId 없음: {}", response.getBody());
            return null;
        } catch (IOException e) {
            log.error("[Curriculum] PDF 읽기 실패: username={}", username, e);
            return null;
        } catch (Exception e) {
            log.error("[Curriculum] 생성 요청 예외: endpoint={}, username={}", endpoint, username, e);
            return null;
        }
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
