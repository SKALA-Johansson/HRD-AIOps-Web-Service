package com.lecture.auth.service;

import com.lecture.auth.dto.ProfileRequest;
import com.lecture.auth.model.Profile;
import com.lecture.auth.model.User;
import com.lecture.auth.repository.ProfileRepository;
import com.lecture.auth.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ProfileService {

    private final ProfileRepository profileRepository;
    private final UserRepository userRepository;

    @Transactional(readOnly = true)
    public Profile getProfileByEmail(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));
        return profileRepository.findByUser(user)
                .orElseThrow(() -> new RuntimeException("Profile not found"));
    }

    @Transactional
    public Profile updateProfileByEmail(String email, ProfileRequest request) {
        User user = userRepository.findByEmail(email)
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
