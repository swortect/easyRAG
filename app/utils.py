
from langchain.embeddings import HuggingFaceBgeEmbeddings
import torch

from dotenv import load_dotenv
import os
# 加载 .env 文件中的环境变量
load_dotenv()
# 从环境变量中获取数据库配置
CACHE_DIR = os.getenv("CACHE_DIR")

class VectorEncoder:
    def __init__(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu") # {'device': 'cuda'} # {'device': 'cpu'}
        print(f"模型运行在{device}")
        model_kwargs = {'device': device}
        encode_kwargs = {'normalize_embeddings': True}  # set True to compute cosine similarity
        self.embed_model = HuggingFaceBgeEmbeddings(model_name=CACHE_DIR+"AI-ModelScope/bge-large-zh-v1___5",
                                                    model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)
    def vectorEncode(self, query: str):
        embed_result = self.embed_model.embed_query(query)
        return embed_result

