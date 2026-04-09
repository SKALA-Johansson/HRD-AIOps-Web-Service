package com.lecture.auth.config;

import com.lecture.auth.model.User;
import com.lecture.auth.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        if (userRepository.count() == 0) {
            // 테스트용 사원 (EMPLOYEE)
            userRepository.save(User.builder()
                    .email("hong@example.com")
                    .password(passwordEncoder.encode("Password123!"))
                    .name("홍길동")
                    .role(User.Role.EMPLOYEE)
                    .build());

            // 테스트용 HR 담당자 (HR)
            userRepository.save(User.builder()
                    .email("hr@example.com")
                    .password(passwordEncoder.encode("Password123!"))
                    .name("관리자")
                    .role(User.Role.HR)
                    .build());

            log.info("테스트 사용자 초기 데이터 생성 완료 (EMPLOYEE, HR)");
        }
    }
}
