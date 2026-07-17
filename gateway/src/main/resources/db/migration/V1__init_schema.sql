CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE collections (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description VARCHAR(2000),
    owner_id UUID NOT NULL REFERENCES users (id),
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE documents (
    id UUID PRIMARY KEY,
    collection_id UUID NOT NULL REFERENCES collections (id),
    filename VARCHAR(500) NOT NULL,
    uploaded_by UUID NOT NULL REFERENCES users (id),
    status VARCHAR(20) NOT NULL,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    uploaded_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_documents_collection_id ON documents (collection_id);

CREATE TABLE query_history (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users (id),
    collection_id UUID,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    mode VARCHAR(20) NOT NULL,
    citations_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_query_history_user_id ON query_history (user_id);
