package com.lecture.report.service;

import com.lecture.report.dto.LearningLogEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
@Slf4j
@RequiredArgsConstructor
public class ActivityLogConsumer {

    // 실제로는 GrowthReportRepository 등을 사용하여 DB에 저장
    @KafkaListener(topics = "learning-logs", groupId = "report-group")
    public void consumeActivityLog(LearningLogEvent event) {
        log.info("Received learning activity for report generation: {}", event);

        if ("Learning.ActivityLogged".equals(event.getEventType())) {
            // 사원의 역량 데이터 분석 및 리포트 갱신 로직 수행
            log.info("Updating growth report for user: {} based on activity: {}", event.getUserId(), event.getActivityType());
            
            // TODO: 핵심 지표 계산 및 리포트 테이블 저장
        }
    }
}
