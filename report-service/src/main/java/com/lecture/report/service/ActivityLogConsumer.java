package com.lecture.report.service;

import com.lecture.report.model.GrowthReport;
import com.lecture.report.repository.GrowthReportRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class ActivityLogConsumer {

    private static final String TOPIC_REPORTING_EVENTS = "reporting-events";
    private static final String TOPIC_HR_ALERT_EVENTS = "hr-alert-events";

    private final GrowthReportRepository growthReportRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    @KafkaListener(topics = "learning-logs", groupId = "report-group")
    public void consumeActivityLog(Map<String, Object> event) {
        log.info("Received learning activity for report generation: {}", event);

        String eventType = stringValue(event.get("event_type"));
        Map<String, Object> payload = payload(event.get("payload"));
        if (payload == null) {
            return;
        }

        // 요청하신 완료 이벤트 기반 리포트 생성/갱신
        if ("Learning.AssignmentCompleted".equals(eventType) || "Learning.QuizCompleted".equals(eventType)) {
            String userId = stringValue(payload.get("user_id"));
            if (userId.isBlank()) {
                return;
            }

            double score = doubleValue(payload.get("score"));
            double maxScore = doubleValue(payload.get("max_score"));
            boolean passed = boolValue(payload.get("passed"));

            GrowthReport report = growthReportRepository.findByUserId(userId)
                    .orElseGet(() -> GrowthReport.builder()
                            .userId(userId)
                            .strengths(List.of())
                            .weaknesses(List.of())
                            .achievementMetrics(new HashMap<>())
                            .build());

            Map<String, Integer> metrics = report.getAchievementMetrics() == null
                    ? new HashMap<>()
                    : new HashMap<>(report.getAchievementMetrics());

            String counterKey = "Learning.AssignmentCompleted".equals(eventType)
                    ? "assignmentsCompleted"
                    : "quizzesCompleted";
            metrics.put(counterKey, metrics.getOrDefault(counterKey, 0) + 1);
            metrics.put("totalCompleted", metrics.getOrDefault("totalCompleted", 0) + 1);
            metrics.put("lastScore", (int) Math.round(score));
            metrics.put("lastMaxScore", (int) Math.round(maxScore));

            int prevCount = metrics.getOrDefault("scoreCount", 0);
            int prevSum = metrics.getOrDefault("scoreSum", 0);
            int newCount = prevCount + 1;
            int newSum = prevSum + (int) Math.round(score);
            metrics.put("scoreCount", newCount);
            metrics.put("scoreSum", newSum);
            metrics.put("averageScore", newCount == 0 ? 0 : Math.round((float) newSum / newCount));

            report.setAchievementMetrics(metrics);
            report.setStrengths(updateSignals(report.getStrengths(), passed,
                    "과제/퀴즈 수행 안정적", "평가 품질 개선 필요"));
            report.setWeaknesses(updateSignals(report.getWeaknesses(), !passed,
                    "평가 품질 개선 필요", "과제/퀴즈 수행 안정적"));

            GrowthReport saved = growthReportRepository.save(report);
            log.info("Growth report updated for user: {}, reportId={}", userId, saved.getId());

            publishReportGenerated(userId, saved.getId(), eventType, passed);
        }
    }

    private void publishReportGenerated(String userId, Long reportId, String triggerEventType, boolean passed) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("user_id", userId);
        payload.put("report_id", String.valueOf(reportId));
        payload.put("trigger_event_type", triggerEventType);
        payload.put("passed", passed);

        Map<String, Object> generatedEvent = new HashMap<>();
        generatedEvent.put("event_type", "Report.Generated");
        generatedEvent.put("event_id", "report-" + reportId + "-" + System.currentTimeMillis());
        generatedEvent.put("timestamp", LocalDateTime.now().toString());
        generatedEvent.put("source", "report-growth-service");
        generatedEvent.put("payload", payload);

        kafkaTemplate.send(TOPIC_REPORTING_EVENTS, generatedEvent);
        log.info("Published report event: {}", generatedEvent);

        Map<String, Object> hrAlertEvent = new HashMap<>();
        hrAlertEvent.put("event_type", "HR.ReportReady");
        hrAlertEvent.put("event_id", "hr-report-" + reportId + "-" + System.currentTimeMillis());
        hrAlertEvent.put("timestamp", LocalDateTime.now().toString());
        hrAlertEvent.put("source", "report-growth-service");
        hrAlertEvent.put("payload", payload);

        kafkaTemplate.send(TOPIC_HR_ALERT_EVENTS, hrAlertEvent);
        log.info("Published HR alert event: {}", hrAlertEvent);
    }

    private List<String> updateSignals(List<String> current, boolean add, String signal, String removeSignal) {
        List<String> items = current == null ? new java.util.ArrayList<>() : new java.util.ArrayList<>(current);
        items.remove(removeSignal);
        if (add && !items.contains(signal)) {
            items.add(signal);
        }
        return items;
    }

    private Map<String, Object> payload(Object payloadObj) {
        if (payloadObj instanceof Map<?, ?> map) {
            Map<String, Object> parsed = new HashMap<>();
            map.forEach((k, v) -> parsed.put(String.valueOf(k), v));
            return parsed;
        }
        return null;
    }

    private String stringValue(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    private boolean boolValue(Object value) {
        if (value instanceof Boolean b) {
            return b;
        }
        return Boolean.parseBoolean(stringValue(value));
    }

    private double doubleValue(Object value) {
        if (value instanceof Number n) {
            return n.doubleValue();
        }
        try {
            return Double.parseDouble(stringValue(value));
        } catch (Exception e) {
            return 0.0;
        }
    }
}
