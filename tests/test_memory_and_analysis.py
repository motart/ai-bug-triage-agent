import tests.bootstrap
from pathlib import Path
from ai_agent.memory import SimpleMemory
from ai_agent.analysis import CodeAnalyzer

class DummyMemory(SimpleMemory):
    def __init__(self):
        self.entries = []
        self.path = Path('noop')
    def _embed(self, text: str):
        return [float(len(text))]
    def save(self):
        pass

def test_memory_search():
    mem = DummyMemory()
    mem.add('bug one', {'f': 'fix1'})
    mem.add('another', {'f': 'fix2'})
    res = mem.search('bug one')
    assert res and res[0]['solution'] == {'f': 'fix1'}

class DummyTokenizer:
    def encode(self, text, return_tensors=None, **kw):
        return [0]
    def decode(self, ids, skip_special_tokens=True):
        return '# Suggested patch:\npatched'

class DummyModel:
    def generate(self, *args, **kwargs):
        return [[0]]

class MemoryStub:
    def __init__(self):
        self.called = False
    def search(self, text, top_k=1):
        return [{'solution': {'file': 'stored patch'}}]
    def add(self, text, fix):
        self.called = True

def test_analyze_bug_generate_patch(tmp_path):
    file = tmp_path / 'file.py'
    file.write_text('code')
    analyzer = CodeAnalyzer.__new__(CodeAnalyzer)
    analyzer.tokenizer = DummyTokenizer()
    analyzer.model = DummyModel()
    analyzer.memory = None
    fix = analyzer.analyze_bug('title', 'desc', [str(file)])
    assert fix[str(file)] == 'patched'

def test_analyze_bug_uses_memory():
    analyzer = CodeAnalyzer.__new__(CodeAnalyzer)
    analyzer.tokenizer = DummyTokenizer()
    analyzer.model = DummyModel()
    mem = MemoryStub()
    analyzer.memory = mem
    fix = analyzer.analyze_bug('t', 'd', [])
    assert fix == {'file': 'stored patch'}
    assert not mem.called
