package com.lecture.content.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lecture.content.domain.ContentType;
import com.lecture.content.dto.ContentRequest;
import com.lecture.content.service.ContentService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.mockito.BDDMockito.willDoNothing;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(ContentController.class)
class ContentControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private ContentService contentService;

    @Test
    @DisplayName("POST /api/v1/contents - Should register content and return 201")
    void registerContentTest() throws Exception {
        willDoNothing().given(contentService).registerContent(any(ContentRequest.class));

        ContentRequest request = ContentRequest.builder()
                .title("New Content")
                .type(ContentType.VIDEO)
                .category("FRONTEND")
                .fileUrl("http://example.com/video.mp4")
                .tags(List.of("react", "hooks"))
                .build();

        mockMvc.perform(post("/api/v1/contents")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value("SUCCESS"))
                .andExpect(jsonPath("$.message").value("Content registered successfully."));
    }

    @Test
    @DisplayName("GET /api/v1/contents - Should list contents with filters")
    void listContentsTest() throws Exception {
        given(contentService.listContents(eq("BACKEND"), eq(ContentType.PDF)))
                .willReturn(List.of(ContentRequest.builder()
                        .title("Sample Backend PDF")
                        .type(ContentType.PDF)
                        .category("BACKEND")
                        .fileUrl("http://example.com/file.pdf")
                        .tags(List.of("java", "spring"))
                        .build()));

        mockMvc.perform(get("/api/v1/contents")
                .param("category", "BACKEND")
                .param("type", "PDF"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("SUCCESS"))
                .andExpect(jsonPath("$.data[0].title").value("Sample Backend PDF"))
                .andExpect(jsonPath("$.data[0].category").value("BACKEND"))
                .andExpect(jsonPath("$.data[0].type").value("PDF"));
    }

    @Test
    @DisplayName("PUT /api/v1/contents/{contentId} - Should update content and return 200")
    void updateContentTest() throws Exception {
        willDoNothing().given(contentService).updateContent(eq(1L), any(ContentRequest.class));

        ContentRequest request = ContentRequest.builder()
                .title("Updated Content")
                .type(ContentType.PDF)
                .category("BACKEND")
                .fileUrl("http://example.com/updated.pdf")
                .tags(List.of("spring", "security"))
                .build();

        mockMvc.perform(put("/api/v1/contents/1")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("SUCCESS"))
                .andExpect(jsonPath("$.message").value("Content updated successfully."));
    }

    @Test
    @DisplayName("DELETE /api/v1/contents/{contentId} - Should delete content and return 200")
    void deleteContentTest() throws Exception {
        willDoNothing().given(contentService).deleteContent(eq(1L));

        mockMvc.perform(delete("/api/v1/contents/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("SUCCESS"))
                .andExpect(jsonPath("$.message").value("Content deleted successfully."));
    }
}
