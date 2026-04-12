package com.lecture.content.controller;

import com.lecture.content.domain.ContentType;
import com.lecture.content.dto.ApiResponse;
import com.lecture.content.dto.ContentRequest;
import com.lecture.content.service.ContentService;
import lombok.extern.slf4j.Slf4j;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/v1/contents")
@Slf4j
@RequiredArgsConstructor
public class ContentController {

    private final ContentService contentService;

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ApiResponse<Void>> uploadContent(
            @RequestParam("file") MultipartFile file,
            @RequestParam("title") String title,
            @RequestParam("category") String category) {
        log.info("Uploading content: {}, category: {}", title, category);
        contentService.uploadAndIngest(file, title, category);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Content uploaded and ingested successfully."));
    }

    @PostMapping(value = "/department-required-pdf", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ApiResponse<Void>> uploadDepartmentRequiredPdf(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "title", required = false) String title,
            @RequestParam(value = "category", required = false) String category) {
        String resolvedTitle = (title != null && !title.isBlank()) ? title : file.getOriginalFilename();
        String resolvedCategory = (category != null && !category.isBlank()) ? category : "부서필수";
        log.info("Uploading department required PDF: {}", resolvedTitle);
        contentService.uploadAndIngest(file, resolvedTitle, resolvedCategory);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Department required PDF uploaded successfully."));
    }

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
