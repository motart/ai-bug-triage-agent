import tests.bootstrap
import base64
from unittest.mock import MagicMock
import requests
import pytest

from ai_agent.connectors.github import GitHubConnector
from ai_agent.connectors.jira import JiraConnector

class FakeResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text
    def json(self):
        return self._json
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError("error", response=self)

def test_jira_get_open_bugs_success(monkeypatch):
    def fake_get(url, params=None, auth=None):
        assert params["jql"].startswith("project=PROJ")
        return FakeResponse(200, json_data={"issues": [{"id": 1}]})
    monkeypatch.setattr(requests, "get", fake_get)
    jira = JiraConnector("http://jira", "u", "t")
    issues = jira.get_open_bugs("proj")
    assert issues == [{"id": 1}]

def test_jira_get_open_bugs_failure(monkeypatch):
    def fake_get(url, params=None, auth=None):
        return FakeResponse(500, text="bad")
    monkeypatch.setattr(requests, "get", fake_get)
    jira = JiraConnector("http://jira", "u", "t")
    with pytest.raises(requests.HTTPError):
        jira.get_open_bugs("proj")

def test_ensure_branch_creates(monkeypatch):
    called = {}
    def fake_get(url, headers=None):
        if url.endswith("heads/new"):
            return FakeResponse(404)
        return FakeResponse(200, json_data={"object": {"sha": "base"}})
    def fake_post(url, json=None, headers=None):
        called["payload"] = json
        return FakeResponse(201)
    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "post", fake_post)
    gh = GitHubConnector("repo", "tok")
    gh.ensure_branch("new")
    assert called["payload"]["sha"] == "base"

def test_ensure_branch_exists(monkeypatch):
    def fake_get(url, headers=None):
        return FakeResponse(200)
    monkeypatch.setattr(requests, "get", fake_get)
    gh = GitHubConnector("repo", "tok")
    gh.ensure_branch("main")

def test_commit_files_create(monkeypatch):
    saved = {}
    def fake_get(url, params=None, headers=None):
        return FakeResponse(404)
    def fake_put(url, json=None, headers=None):
        saved.update(json)
        return FakeResponse(200)
    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "put", fake_put)
    gh = GitHubConnector("repo", "tok")
    gh.commit_files("br", {"a.txt": "hello"}, "msg")
    assert base64.b64decode(saved["content"]).decode() == "hello"
    assert saved["branch"] == "br"

def test_commit_files_update(monkeypatch):
    saved = {}
    def fake_get(url, params=None, headers=None):
        return FakeResponse(200, json_data={"sha": "123"})
    def fake_put(url, json=None, headers=None):
        saved.update(json)
        return FakeResponse(200)
    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "put", fake_put)
    gh = GitHubConnector("repo", "tok")
    gh.commit_files("br", {"a.txt": "hello"}, "msg")
    assert saved["sha"] == "123"

def test_create_pull_request(monkeypatch):
    def fake_post(url, json=None, headers=None):
        return FakeResponse(201, json_data={"html_url": "url"})
    monkeypatch.setattr(requests, "post", fake_post)
    gh = GitHubConnector("repo", "tok")
    res = gh.create_pull_request("t", "h", "b", "d")
    assert res["html_url"] == "url"

def test_search_code(monkeypatch):
    def fake_get(url, params=None, headers=None):
        if "first" in params["q"]:
            return FakeResponse(200, json_data={"items": [{"path": "a"}, {"path": "b"}]})
        if "second" in params["q"]:
            return FakeResponse(200, json_data={"items": [{"path": "a"}, {"path": "c"}]})
        return FakeResponse(500)
    monkeypatch.setattr(requests, "get", fake_get)
    gh = GitHubConnector("repo", "tok")
    files = gh.search_code(["first", "second"])
    assert files == ["a", "b", "c"]
