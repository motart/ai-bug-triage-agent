import sys
import types

# websocket client stub
if 'websocket' not in sys.modules:
    ws_mod = types.ModuleType('websocket')
    ws_mod.WebSocketApp = object
    sys.modules['websocket'] = ws_mod

# torch stub
if 'torch' not in sys.modules:
    torch_mod = types.ModuleType('torch')
    class _Ctx:
        def __enter__(self):
            pass
        def __exit__(self, exc_type, exc, tb):
            pass
    def no_grad():
        return _Ctx()
    torch_mod.no_grad = no_grad
    sys.modules['torch'] = torch_mod

# transformers stub
if 'transformers' not in sys.modules:
    tr_mod = types.ModuleType('transformers')
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
    tr_mod.AutoTokenizer = type("AutoTokenizer", (), {"from_pretrained": classmethod(lambda cls, *a, **kw: DummyTokenizer())})
    tr_mod.AutoModelForCausalLM = type("AutoModelForCausalLM", (), {"from_pretrained": classmethod(lambda cls, *a, **kw: DummyModel())})
    tr_mod.AutoModel = type("AutoModel", (), {"from_pretrained": classmethod(lambda cls, *a, **kw: DummyModel())})
    sys.modules['transformers'] = tr_mod

# llama_index and faiss stubs
if 'llama_index' not in sys.modules:
    li = types.ModuleType('llama_index')
    li.Document = lambda text, metadata=None: types.SimpleNamespace(text=text, metadata=metadata or {})
    li.ServiceContext = types.SimpleNamespace(from_defaults=lambda **kw: None)
    li.StorageContext = types.SimpleNamespace(from_defaults=lambda **kw: None)
    class VectorStoreIndex:
        def __init__(self, *a, **kw):
                self.storage_context = types.SimpleNamespace(persist=lambda d: None)
        @classmethod
        def load_from_persist_dir(cls, *a, **kw):
            return cls()
        def as_query_engine(self, similarity_top_k=1):
            return types.SimpleNamespace(query=lambda text: types.SimpleNamespace(source_nodes=[]))
    li.VectorStoreIndex = VectorStoreIndex
    sys.modules['llama_index'] = li

if 'faiss' not in sys.modules:
    sys.modules['faiss'] = types.ModuleType('faiss')

# submodules for llama_index
if 'llama_index.embeddings.huggingface' not in sys.modules:
    sub = types.ModuleType('llama_index.embeddings.huggingface')
    class HF:
        def __init__(self, *a, **kw):
            self.embedding_size = 1
    sub.HuggingFaceEmbedding = HF
    sys.modules['llama_index.embeddings.huggingface'] = sub

if 'llama_index.vector_stores.faiss' not in sys.modules:
    sub = types.ModuleType('llama_index.vector_stores.faiss')
    class FS:
        def __init__(self, *a, **kw):
            pass
        @classmethod
        def from_persist_dir(cls, *a, **kw):
            return cls()
    sub.FaissVectorStore = FS
    sys.modules['llama_index.vector_stores.faiss'] = sub
