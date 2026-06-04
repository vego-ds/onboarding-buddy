import pytest
from fastapi import HTTPException

from backend.routes import assistant as assistant_route
from backend.services import assistant_service
from schemas.assistant import AssistantChatRequest


def test_normalize_role_preserves_acronym_roles():
    assert assistant_service.normalize_role("hr") == "HR"
    assert assistant_service.normalize_role(" IT ") == "IT"
    assert assistant_service.normalize_role("security") == "Security"
    assert assistant_service.normalize_role("unknown") == "Employee"


def test_retrieve_knowledge_returns_relevant_approved_sources():
    sections = assistant_service.retrieve_knowledge(
        "What should IT do for laptop access?",
        "IT",
    )

    assert sections
    combined_text = " ".join(
        f"{section['title']} {section['content']}" for section in sections
    ).lower()
    assert "laptop" in combined_text or "access" in combined_text
    assert "relevance_score" in sections[0]
    assert sections[0]["retrieval_mode"] in {"vector_index", "local_vector_fallback"}


def test_build_knowledge_chunks_adds_embeddings_and_chunk_ids():
    chunks = assistant_service.build_knowledge_chunks()

    assert chunks
    assert chunks[0]["chunk_id"].startswith("KNOW_")
    assert len(chunks[0]["embedding"]) == assistant_service.EMBEDDING_DIMENSIONS


def test_sync_knowledge_index_upserts_chunks(monkeypatch):
    saved_chunks = []

    def fake_upsert(**kwargs):
        saved = {
            "chunk_id": assistant_service.make_chunk_id(
                kwargs["source"],
                kwargs["content_hash"],
            ),
            **kwargs,
        }
        saved_chunks.append(saved)
        return saved

    monkeypatch.setattr(assistant_service, "upsert_knowledge_chunk", fake_upsert)
    monkeypatch.setattr(
        assistant_service,
        "delete_stale_knowledge_chunks",
        lambda active_chunk_ids: 0,
    )

    response = assistant_service.sync_knowledge_index()

    assert response["status"] == "indexed"
    assert response["chunk_count"] == len(saved_chunks)
    assert response["sources"]


def test_low_confidence_question_escalates_without_llm(monkeypatch):
    monkeypatch.setattr(
        assistant_service,
        "retrieve_knowledge",
        lambda *_args, **_kwargs: [
            {
                "title": "Unrelated",
                "source": "policies.md",
                "content": "Employees should complete onboarding tasks.",
                "relevance_score": 0.01,
                "retrieval_mode": "local_vector_fallback",
            }
        ],
    )
    monkeypatch.setattr(
        assistant_service,
        "synthesize_answer",
        lambda *_args, **_kwargs: "This should not be called.",
    )

    response = assistant_service.answer_onboarding_question(
        question="What is the company stock forecast?",
        user_role="Employee",
    )

    assert response["used_llm"] is False
    assert response["needs_escalation"] is True
    assert response["confidence_label"] == "insufficient"
    assert "do not have enough approved onboarding knowledge" in response["answer"]


def test_assistant_uses_deterministic_fallback_when_llm_unavailable(monkeypatch):
    def unavailable_llm(*_args, **_kwargs):
        raise RuntimeError("LLM unavailable")

    monkeypatch.setattr(assistant_service, "synthesize_answer", unavailable_llm)

    response = assistant_service.answer_onboarding_question(
        question="What should I do during my first week?",
        user_role="Employee",
    )

    assert response["user_role"] == "Employee"
    assert response["used_llm"] is False
    assert response["sources"]
    assert "approved onboarding knowledge" in response["answer"].lower()
    assert response["citations"]
    assert response["confidence_score"] >= 0


def test_assistant_reports_llm_synthesis_when_available(monkeypatch):
    monkeypatch.setattr(
        assistant_service,
        "retrieve_knowledge",
        lambda *_args, **_kwargs: [
                {
                    "title": "Manager Checklist",
                    "source": "role_guides.md",
                    "content": "Managers should review onboarding progress.",
                    "relevance_score": 0.8,
                    "retrieval_mode": "local_vector_fallback",
                }
        ],
    )
    monkeypatch.setattr(
        assistant_service,
        "synthesize_answer",
        lambda *_args, **_kwargs: "Use the approved onboarding checklist. [1]",
    )

    response = assistant_service.answer_onboarding_question(
        question="What should managers review?",
        user_role="Manager",
    )

    assert response["user_role"] == "Manager"
    assert response["used_llm"] is True
    assert response["answer"] == "Use the approved onboarding checklist. [1]"
    assert response["confidence_label"] == "high"


def test_assistant_returns_employee_not_found_without_llm(monkeypatch):
    monkeypatch.setattr(assistant_service, "get_employee_by_id", lambda _employee_id: None)

    response = assistant_service.answer_onboarding_question(
        question="What is next for this employee?",
        user_role="HR",
        employee_id="EMP_MISSING",
    )

    assert response["answer"] == "Employee not found."
    assert response["user_role"] == "HR"
    assert response["sources"] == []
    assert response["citations"] == []
    assert response["used_llm"] is False
    assert response["needs_escalation"] is True


def test_assistant_route_rejects_empty_question():
    request = AssistantChatRequest(question="   ", user_role="Employee")

    with pytest.raises(HTTPException) as error:
        assistant_route.chat_with_assistant(request)

    assert error.value.status_code == 400
    assert error.value.detail == "Question is required."


def test_assistant_route_delegates_chat_request(monkeypatch):
    calls = {}

    def fake_answer(question, user_role="Employee", employee_id=None):
        calls["question"] = question
        calls["user_role"] = user_role
        calls["employee_id"] = employee_id
        return {"answer": "done"}

    monkeypatch.setattr(assistant_route, "answer_onboarding_question", fake_answer)

    request = AssistantChatRequest(
        question=" What is next? ",
        user_role="HR",
        employee_id="EMP_12345678",
    )
    response = assistant_route.chat_with_assistant(request)

    assert calls == {
        "question": "What is next?",
        "user_role": "HR",
        "employee_id": "EMP_12345678",
    }
    assert response == {"answer": "done"}


def test_assistant_route_reindexes_knowledge(monkeypatch):
    monkeypatch.setattr(
        assistant_route,
        "sync_knowledge_index",
        lambda: {"status": "indexed", "chunk_count": 3},
    )

    response = assistant_route.reindex_assistant_knowledge()

    assert response == {"status": "indexed", "chunk_count": 3}
