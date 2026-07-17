package com.cortex.gateway.exception;

/** Wraps a failure talking to ai-service (network error, non-2xx response, timeout). */
public class AiServiceException extends RuntimeException {
    public AiServiceException(String message, Throwable cause) {
        super(message, cause);
    }
}
