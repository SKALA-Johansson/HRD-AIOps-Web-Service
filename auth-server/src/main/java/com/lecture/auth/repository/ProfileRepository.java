package com.lecture.auth.repository;

import com.lecture.auth.model.Profile;
import com.lecture.auth.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ProfileRepository extends JpaRepository<Profile, String> {
    Optional<Profile> findByUser(User user);
    Optional<Profile> findByUserUserId(String userId);
}
