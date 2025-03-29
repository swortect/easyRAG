from modelscope.hub.snapshot_download import snapshot_download
from dotenv import load_dotenv
import os
# 加载 .env 文件中的环境变量
load_dotenv()
# 从环境变量中获取数据库配置
CACHE_DIR = os.getenv("CACHE_DIR")
emb_model_dir = snapshot_download('AI-ModelScope/bge-large-zh-v1.5', cache_dir=CACHE_DIR)
