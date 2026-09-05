import httpx


MEMORY_URL = "http://memory:8000"


def test_get_or_create_conversation_without_id_generates_conversation():
    response = httpx.post(
        f"{MEMORY_URL}/conversations/get_or_create",
        json={"conversation_id": None},
    )

    response.raise_for_status()
    conversation = response.json()["conversation"]

    assert conversation["id"]
    assert conversation["messages"] == []


def test_save_and_get_conversation():
    conversation = {
        "id": "test-memory-conversation",
        "messages": [
            {"role": "user", "content": "mensaje guardado"},
        ],
    }

    save_response = httpx.post(
        f"{MEMORY_URL}/conversations/save",
        json={"conversation": conversation},
    )

    save_response.raise_for_status()
    assert save_response.json() == {"success": True}

    get_response = httpx.post(
        f"{MEMORY_URL}/conversations/get_or_create",
        json={"conversation_id": conversation["id"]},
    )

    get_response.raise_for_status()
    saved_conversation = get_response.json()["conversation"]

    assert saved_conversation["id"] == conversation["id"]
    assert saved_conversation["messages"][0]["role"] == "user"
    assert saved_conversation["messages"][0]["content"] == "mensaje guardado"