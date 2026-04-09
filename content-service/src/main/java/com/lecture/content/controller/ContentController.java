package com.lecture.content.controller;

import com.lecture.content.domain.ContentType;
import com.lecture.content.dto.ApiResponse;
import com.lecture.content.dto.ContentRequest;
import com.lecture.content.service.ContentService;
import lombok.extern.slf4j.Slf4j;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/contents")
@Slf4j
@RequiredArgsConstructor
public class ContentController {

    private final ContentService contentService;

    @PostMapping
    public ResponseEntity<ApiResponse<Void>> registerContent(@RequestBody ContentRequest request) {
        log.info("Registering content: {}", request.getTitle());
        contentService.registerContent(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Content registered successfully."));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<ContentRequest>>> listContents(
            @RequestParam(required = false) String category,
            @RequestParam(required = false) ContentType type) {
        log.info("Listing contents with category: {} and type: {}", category, type);
        return ResponseEntity.ok(ApiResponse.success("Success", contentService.listContents(category, type)));
    }

    @PutMapping("/{contentId}")
    public ResponseEntity<ApiResponse<Void>> updateContent(
            @PathVariable Long contentId,
            @RequestBody ContentRequest request) {
        log.info("Updating content with ID: {}", contentId);
        contentService.updateContent(contentId, request);
        return ResponseEntity.ok(ApiResponse.success("Content updated successfully."));
    }

    @DeleteMapping("/{contentId}")
    public ResponseEntity<ApiResponse<Void>> deleteContent(@PathVariable Long contentId) {
        log.info("Deleting content with ID: {}", contentId);
        contentService.deleteContent(contentId);
        return ResponseEntity.ok(ApiResponse.success("Content deleted successfully."));
    }
}
