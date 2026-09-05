COMPOSE=docker compose

.PHONY: up down build restart logs ps clean shell

up:
	docker compose up \
		nginx \
		agent \
		llm \
		tools-executor \
		memory \
		ollama \
		mcp-filesystem

build:
	$(COMPOSE) up --build

up-d:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) down
	$(COMPOSE) up -d

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

clean:
	$(COMPOSE) down --volumes --remove-orphans


test:
	@OLLAMA_BASE_URL=http://fake-llm:8000 docker compose up -d \
		agent fake-llm tools-executor memory mcp-filesystem \
		>/tmp/chatbot-compose.log 2>&1
	@OLLAMA_BASE_URL=http://fake-llm:8000 docker compose run --rm test-runner \
		pytest -q --tb=short \
		>/tmp/chatbot-test.log 2>&1; \
	status=$$?; \
	docker compose rm -sf fake-llm  \
		>/dev/null 2>&1; \
	if [ $$status -eq 0 ]; then \
		echo "TESTS PASSED"; \
	else \
		echo "TESTS FAILED"; \
		grep -E '^(FAILED|ERROR|[0-9]+ failed|[0-9]+ passed|E   )' \
			/tmp/chatbot-test.log; \
	fi; \
	rm -f /tmp/chatbot-test.log /tmp/chatbot-compose.log; \
	exit $$status

test-verbose:
	OLLAMA_BASE_URL=http://fake-llm:8000 docker compose up -d \
		agent fake-llm tools-executor memory mcp-filesystem

	OLLAMA_BASE_URL=http://fake-llm:8000 docker compose run --rm test-runner \
		pytest -vv --tb=long; \
	status=$$?; \
	docker compose rm -sf fake-llm; \
	exit $$status