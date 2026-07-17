package com.cortex.gateway;

import java.nio.file.Path;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * Base for gateway integration tests that need a real Postgres instance (for Flyway-managed
 * schema and JPA behavior that H2/mocks can't faithfully reproduce - e.g. jsonb columns, unique
 * constraints). ai-service is deliberately left unreachable here: only endpoints that don't call
 * out to it (auth, collections, document upload/status) are covered by these tests.
 *
 * <p>Deliberately NOT using {@code @Testcontainers}/{@code @Container}: that annotation pair stops
 * the container after each test class, but since {@code POSTGRES} is a static field declared here
 * and inherited (not redeclared) by every subclass, all subclasses share the exact same field/
 * container instance. Combined with Spring's TestContext caching (which reuses one
 * ApplicationContext - and its Hikari pool bound to a specific container port - across test classes
 * with identical config), a per-class stop+restart leaves later test classes holding a cached
 * DataSource pointed at a port from a container that's already been torn down. This is the
 * documented Testcontainers "singleton container" pattern: start once in a static initializer and
 * let Ryuk reap it at JVM exit instead.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.MOCK)
@AutoConfigureMockMvc
public abstract class AbstractIntegrationTest {

    static final PostgreSQLContainer<?> POSTGRES = new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("cortex")
            .withUsername("cortex")
            .withPassword("cortex");

    static {
        POSTGRES.start();
    }

    @TempDir
    static Path uploadsDir;

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", POSTGRES::getJdbcUrl);
        registry.add("spring.datasource.username", POSTGRES::getUsername);
        registry.add("spring.datasource.password", POSTGRES::getPassword);
        registry.add("cortex.uploads.dir", () -> uploadsDir.toString());
        registry.add("cortex.ai-service.base-url", () -> "http://localhost:1");
    }
}
