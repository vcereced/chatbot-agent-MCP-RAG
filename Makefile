COMPOSE=docker compose

.PHONY: up down build restart logs ps clean shell

up:
	$(COMPOSE) up

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

shell:
	$(COMPOSE) exec chatbot bash