package com.cortex.gateway.web;

import com.cortex.gateway.dto.history.QueryHistoryDto;
import com.cortex.gateway.dto.query.QueryRequestDto;
import com.cortex.gateway.dto.query.QueryResponseDto;
import com.cortex.gateway.security.CortexPrincipal;
import com.cortex.gateway.service.QueryService;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/query")
public class QueryController {

    private final QueryService queryService;

    public QueryController(QueryService queryService) {
        this.queryService = queryService;
    }

    @PostMapping
    public QueryResponseDto ask(
            @AuthenticationPrincipal CortexPrincipal principal, @Valid @RequestBody QueryRequestDto request) {
        return queryService.ask(principal.userId(), request);
    }

    @GetMapping("/history")
    public List<QueryHistoryDto> history(@AuthenticationPrincipal CortexPrincipal principal) {
        return queryService.history(principal.userId());
    }
}
