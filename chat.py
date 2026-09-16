import os
import sys


DEFAULT_MODEL = "gpt-5.5"
DEFAULT_ENV_FILES = (".env", ".env.example")


def _get_text(response):
    text = getattr(response, "output_text", None)
    if text:
        return text
    return str(response)


def _create_default_client(api_key):
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def _load_env_file(path):
    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            os.environ.setdefault(key, value)


def _load_env_files(paths):
    for path in paths:
        _load_env_file(path)


def _get_api_key():
    return os.environ.get("LLM_API_KEY")


def _ensure_api_key():
    if _get_api_key():
        return True

    print("LLM_API_KEY is required. Set it before running the chat CLI.", file=sys.stderr)
    return False


def _ask_once(client, model, prompt, previous_response_id=None):
    kwargs = {"model": model, "input": prompt}
    if previous_response_id:
        kwargs["previous_response_id"] = previous_response_id

    response = client.responses.create(**kwargs)
    return response, _get_text(response)


def _interactive_chat(client, model):
    print(f"Chatting with {model}. Type 'exit' or 'quit' to leave.")
    previous_response_id = None

    while True:
        try:
            prompt = input("> ").strip()
        except EOFError:
            print()
            return 0

        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            return 0

        response, text = _ask_once(client, model, prompt, previous_response_id)
        previous_response_id = getattr(response, "id", None)
        print(text)


def main(argv=None, client_factory=_create_default_client, env_files=DEFAULT_ENV_FILES):
    argv = list(sys.argv[1:] if argv is None else argv)
    _load_env_files(env_files)

    if not _ensure_api_key():
        return 2

    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    client = client_factory(_get_api_key())

    if argv:
        prompt = " ".join(argv)
        _, text = _ask_once(client, model, prompt)
        print(text)
        return 0

    return _interactive_chat(client, model)


if __name__ == "__main__":
    raise SystemExit(main())
