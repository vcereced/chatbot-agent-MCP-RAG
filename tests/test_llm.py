import httpx


LLM_URL = "http://llm:8000"


def test_generate_text_with_fake_llm():
    response = httpx.post(
        f"{LLM_URL}/generate",
        json={
            "messages": [
                {"role": "user", "content": "test mensaje"},
            ],
            "tools": [],
        },
    )

    response.raise_for_status()
    result = response.json()["result"]

    assert result["text"] == "test mensaje ok"
    assert result["tool_call"] is None

def test_generate_tool_call_with_fake_llm():
    response = httpx.post(
        f"{LLM_URL}/generate",
        json={
            "messages": [
                {"role": "user", "content": "test tool"},
            ],
            "tools": [],
        },
    )

    response.raise_for_status()
    result = response.json()["result"]

    assert result["text"] is None
    assert result["tool_call"]["name"] == "calculator"
    assert result["tool_call"]["arguments"] == {"expression": "2 + 2"}