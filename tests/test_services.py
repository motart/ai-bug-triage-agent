import tests.bootstrap
from unittest.mock import MagicMock

from bug_analyzer_service import service as bas
from code_learner_service import service as cls
from ai_agent import webhook_server as ws


def test_bug_analyze_endpoint(monkeypatch):
    bas.analyzer = MagicMock()
    bas.analyzer.analyze_bug.return_value = {"f": "fix"}
    client = bas.app.test_client()
    resp = client.post("/analyze", json={"title": "t", "description": "d", "files": []})
    assert resp.get_json() == {"f": "fix"}
    bas.analyzer.analyze_bug.assert_called_with("t", "d", [])


def test_bug_remember_endpoint(monkeypatch):
    bas.analyzer = MagicMock()
    client = bas.app.test_client()
    resp = client.post("/remember", json={"title": "t", "description": "d", "fix": {}})
    assert resp.get_json() == {"status": "stored"}
    bas.analyzer.remember.assert_called_with("t", "d", {})


def test_code_learner_learn(monkeypatch):
    cls.vector_index = MagicMock()
    client = cls.app.test_client()
    resp = client.post("/learn", json={"file": "x.py", "content": "code"})
    assert resp.status_code == 200
    assert cls.code_memory["x.py"] == "code"
    cls.vector_index.add_code.assert_called_with("x.py", "code")


def test_code_learner_memory_endpoint():
    client = cls.app.test_client()
    cls.code_memory["a"] = "b"
    resp = client.get("/memory")
    assert resp.get_json()["a"] == "b"


def test_code_learner_query(monkeypatch):
    cls.vector_index = MagicMock()
    cls.vector_index.query.return_value = ["a.py"]
    client = cls.app.test_client()
    resp = client.post("/query", json={"query": "text"})
    assert resp.get_json() == {"files": ["a.py"]}
    cls.vector_index.query.assert_called_with("text")


def test_code_generation(monkeypatch):
    monkeypatch.setattr(cls, "generate_code", lambda prompt: "gen")
    client = cls.app.test_client()
    resp = client.post("/generate", json={"prompt": "p"})
    assert resp.get_json() == {"completion": "gen"}


def test_webhook_process(monkeypatch):
    ws.agent = MagicMock()
    client = ws.app.test_client()
    issue = {"key": "BUG-1", "fields": {"issuetype": {"name": "Bug"}}}
    resp = client.post("/webhook", json={"issue": issue, "issue_event_type_name": "created"})
    assert resp.get_json()["status"] == "processed"
    ws.agent.process_bug.assert_called_with(issue)
