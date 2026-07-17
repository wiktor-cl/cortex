package com.cortex.gateway.web;

import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.cortex.gateway.AbstractIntegrationTest;
import com.cortex.gateway.dto.auth.RegisterRequest;
import com.cortex.gateway.dto.collection.CreateCollectionRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;

/**
 * Exercises the full register -> authenticate -> create collection -> upload document -> internal
 * status callback path against a real Postgres container, verifying JWT auth, role-based access
 * control (ADMIN-only endpoints), and the internal-API-key-guarded worker callback all wired up
 * correctly end to end.
 */
class AuthenticationFlowIntegrationTest extends AbstractIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void unauthenticatedRequestToProtectedEndpointIsRejected() throws Exception {
        mockMvc.perform(get("/api/collections")).andExpect(status().isUnauthorized());
    }

    @Test
    void fullUserJourneyRegisterCreateCollectionUploadDocument() throws Exception {
        String email = "engineer-" + System.nanoTime() + "@example.com";
        String registerBody = objectMapper.writeValueAsString(new RegisterRequest(email, "password123"));

        String registerResponse = mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(registerBody))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.email").value(email))
                .andReturn()
                .getResponse()
                .getContentAsString();
        String token = objectMapper.readTree(registerResponse).get("token").asText();

        String createCollectionBody =
                objectMapper.writeValueAsString(new CreateCollectionRequest("Manuals", "Ops manuals"));
        String collectionResponse = mockMvc.perform(post("/api/collections")
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createCollectionBody))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("Manuals"))
                .andReturn()
                .getResponse()
                .getContentAsString();
        String collectionId = objectMapper.readTree(collectionResponse).get("id").asText();

        mockMvc.perform(get("/api/collections")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()", greaterThanOrEqualTo(1)));

        MockMultipartFile file =
                new MockMultipartFile("file", "manual.pdf", "application/pdf", "content".getBytes());
        String documentResponse = mockMvc.perform(multipart("/api/collections/" + collectionId + "/documents")
                        .file(file)
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value("QUEUED"))
                .andReturn()
                .getResponse()
                .getContentAsString();
        String documentId = objectMapper.readTree(documentResponse).get("id").asText();

        mockMvc.perform(get("/api/admin/stats").header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());

        mockMvc.perform(patch("/internal/documents/" + documentId + "/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"DONE\",\"chunkCount\":4}"))
                .andExpect(status().isUnauthorized());

        mockMvc.perform(patch("/internal/documents/" + documentId + "/status")
                        .header("X-Internal-Api-Key", "change-me-internal-key")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"DONE\",\"chunkCount\":4}"))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/api/documents/" + documentId).header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("DONE"))
                .andExpect(jsonPath("$.chunkCount").value(4));
    }

    @Test
    void adminEndpointsAreOnlyReachableByDefaultSeededAdmin() throws Exception {
        String loginBody = objectMapper.writeValueAsString(
                new com.cortex.gateway.dto.auth.LoginRequest("admin@cortex.local", "changeme123"));
        String loginResponse = mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(loginBody))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();
        String adminToken = objectMapper.readTree(loginResponse).get("token").asText();

        mockMvc.perform(get("/api/admin/stats").header("Authorization", "Bearer " + adminToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.userCount", greaterThanOrEqualTo(1)));
    }
}
