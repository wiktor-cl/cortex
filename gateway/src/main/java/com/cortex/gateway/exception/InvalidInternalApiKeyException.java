package com.cortex.gateway.exception;

public class InvalidInternalApiKeyException extends RuntimeException {
    public InvalidInternalApiKeyException() {
        super("Missing or invalid internal API key");
    }
}
