package com.lecture.curriculum;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@EnableDiscoveryClient
@SpringBootApplication
public class CurriculumApplication {
    public static void main(String[] args) {
        SpringApplication.run(CurriculumApplication.class, args);
    }
}
