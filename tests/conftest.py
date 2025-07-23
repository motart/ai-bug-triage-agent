import sys
import types
import pytest

@pytest.fixture(autouse=True)
def stub_heavy_deps(monkeypatch):
    if 'torch' not in sys.modules:
        torch = types.ModuleType('torch')
        class _Ctx:
            def __enter__(self):
                pass
            def __exit__(self, exc_type, exc, tb):
                pass
        def no_grad():
            return _Ctx()
        torch.no_grad = no_grad
        sys.modules['torch'] = torch
    if 'transformers' not in sys.modules:
        transformers = types.ModuleType('transformers')
        class DummyTokenizer:
            def encode(self, text, return_tensors=None, **kw):
                return [0]
            def __call__(self, *args, **kw):
                return {'input_ids': [0]}
            def decode(self, ids, skip_special_tokens=True):
                return 'text'
        class DummyModel:
            def generate(self, *args, **kwargs):
                return [[0]]
            def __call__(self, *args, **kwargs):
                class O:
                    last_hidden_state = types.SimpleNamespace(mean=lambda dim: [0])
                return O()
        transformers.AutoTokenizer = types.SimpleNamespace(from_pretrained=lambda *a, **kw: DummyTokenizer())
        transformers.AutoModelForCausalLM = types.SimpleNamespace(from_pretrained=lambda *a, **kw: DummyModel())
        transformers.AutoModel = types.SimpleNamespace(from_pretrained=lambda *a, **kw: DummyModel())
        sys.modules['transformers'] = transformers
    if 'llama_index' not in sys.modules:
        li = types.ModuleType('llama_index')
        li.Document = lambda text, metadata=None: types.SimpleNamespace(text=text, metadata=metadata or {})
        li.ServiceContext = types.SimpleNamespace(from_defaults=lambda **kw: None)
        li.StorageContext = types.SimpleNamespace(from_defaults=lambda **kw: None)
        li.VectorStoreIndex = types.SimpleNamespace(
            load_from_persist_dir=lambda *a, **kw: types.SimpleNamespace(
                as_query_engine=lambda similarity_top_k=1: types.SimpleNamespace(query=lambda text: types.SimpleNamespace(source_nodes=[]))
            )
        )
        sys.modules['llama_index'] = li
    if 'faiss' not in sys.modules:
        sys.modules['faiss'] = types.ModuleType('faiss')
