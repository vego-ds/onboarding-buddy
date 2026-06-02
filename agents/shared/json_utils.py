import json


def parse_json_object(raw_response: str) -> dict:
    if not raw_response:
        raise ValueError("LLM returned an empty response.")

    decoder = json.JSONDecoder()
    response_text = raw_response.strip()

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, dict):
        return parsed

    for index, character in enumerate(response_text):
        if character != "{":
            continue

        try:
            candidate, _ = decoder.raw_decode(response_text[index:])
        except json.JSONDecodeError:
            continue

        if isinstance(candidate, dict):
            return candidate

    raise ValueError("LLM response did not contain a valid JSON object.")
