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
            User user = User.builder()
                    .username("3021")
                    .password(passwordEncoder.encode("021210"))
                    .name("이지수")
                    .role(User.Role.EMPLOYEE)
                    .build();
            userRepository.save(user);

            User hr = User.builder()
                    .username("hr")
                    .password(passwordEncoder.encode("1234"))
                    .name("인사담당자")
                    .role(User.Role.HR)
                    .build();
            userRepository.save(hr);

            log.info("테스트 사용자 초기 데이터 생성 완료 (EMPLOYEE, HR)");
        }
    }
}
