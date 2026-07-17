-- ai-service stores embeddings in its own "rag" schema (created at app startup); gateway owns
-- the default "public" schema via Flyway. Both share this one Postgres instance/database, kept
-- apart purely by schema, which is enough isolation for a project this size.
CREATE EXTENSION IF NOT EXISTS vector;
