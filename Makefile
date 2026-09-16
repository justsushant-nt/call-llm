.PHONY: chat ask test

PYTHON ?= python3

chat:
	$(if $(MODEL),OPENAI_MODEL="$(MODEL)") uv run --with openai $(PYTHON) chat.py

ask:
	@test -n "$(PROMPT)" || (echo 'Usage: make ask PROMPT="your question"' >&2; exit 2)
	$(if $(MODEL),OPENAI_MODEL="$(MODEL)") uv run --with openai $(PYTHON) chat.py "$(PROMPT)"

test:
	$(PYTHON) -m unittest discover -s tests
