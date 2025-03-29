from fastapi import APIRouter,Request,File, UploadFile, BackgroundTasks
from tortoise import Tortoise
from app.models import Knowledge,KnowledgeFile,Agent,Scene
import os
import hashlib
import json
import asyncio
from langchain_community.document_loaders import TextLoader,CSVLoader,PyPDFLoader,UnstructuredMarkdownLoader,JSONLoader
from langchain_core.documents import Document as langDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
import time
from readability import Document
from bs4 import BeautifulSoup
import requests
import re
from pydantic import BaseModel


class SearchRequest(BaseModel):
    q: str=""
    agent_id: int=0
    scene_id: int=0
    file_id: int=0



router = APIRouter()

class CustomTextLoader:
    def __init__(self, text: str):
        self.text = text

    def load(self):
        # 创建 Document 对象并返回
        return [langDocument(page_content=self.text)]
async def get_embedding_from_text(text: str) -> list[float]:
    # 这里可以替换为实际的嵌入向量生成逻辑，例如调用 OpenAI API
    return [0.1] * 1024

def jsonReturn(info="",status=0,data=[]):
    return {"status": status,"info": info,"data": data}


def clean_string(input_string):
    # 去除换行符和制表符
    cleaned_string = input_string.replace("\n", "").replace("\t", "")
    # 替换多个空格为单个空格
    cleaned_string = re.sub(r"\s+", " ", cleaned_string)
    # 替换中文字符之间的空格为单个空格（可选，根据需求调整）
    cleaned_string = re.sub(r"(\S)\s+(\S)", r"\1 \2", cleaned_string)
    # 去除首尾空格
    cleaned_string = cleaned_string.strip()
    return cleaned_string


def check_video_and_text_length(content_html):
    # 解析HTML内容
    soup = BeautifulSoup(content_html, "html.parser")
    # 检查是否存在视频播放器标签
    return soup.find_all(['video', 'iframe', 'object', 'embed'])

async def getVectorEncode(text,insertDict,file_index,request):
    result = request.app.vectorEncoderInstance.vectorEncode(text)
    k_obj=await Knowledge.create(k_text=text,
                                 vector_code=result,
                                 agent_id=insertDict['agent_id'],
                                 user_id=insertDict['user_id'],
                                 scene_id=insertDict['scene_id'],
                                 file_id=insertDict['file_id'],
                                 file_url=insertDict['file_url'],
                                 file_index=file_index
                                 )
    print("save ok")
    return result
async def process_text_file(insertDict, request,file_path: str="",file_content: str=""):
    # 加载文本文件
    chunk_size=300
    chunk_overlap=20
    print("开始分割")
    start_time = time.time()
    if file_content:
        print("正文")
        loader = CustomTextLoader(file_content)
        docs = loader.load()
        # 块大小200字为一组，每组之间20字重叠
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_documents(docs)  # 分割成块
    else:
        print("路径")
        file_suffix = os.path.splitext(file_path)[1][1:]
        print(file_suffix)

        if file_suffix=="txt":
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            # 块大小200字为一组，每组之间20字重叠
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            chunks = text_splitter.split_documents(docs)  # 分割成块
        elif file_suffix=="csv":
            loader = CSVLoader(file_path)
            chunks = loader.load()
        elif file_suffix == "pdf":
            loader = PyPDFLoader(file_path)
            chunks = loader.load_and_split()
            file_content=''.join([chunk.page_content for chunk in chunks])
            loader = CustomTextLoader(file_content)
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            chunks = text_splitter.split_documents(docs)  # 分割成块
    print("分割完成")
    chunks_time = time.time()
    splitter_time = chunks_time-start_time
    print("并发上传")
    tasks = [getVectorEncode(clean_string(doc.page_content),insertDict,file_index, request) for file_index, doc in enumerate(chunks)]
    results = await asyncio.gather(*tasks)  # 并发执行所有任务
    print("上传完成")
    end_time = time.time()
    take_time=end_time-start_time
    # 删除文件（可选）

    if file_path:
        print("删除原文件")
        os.remove(file_path)
    print("开始发送消息")

    kf_obj = await KnowledgeFile.get(id=insertDict["file_id"])  # 假设 file_hash 是唯一的
    # 更新 embedding_status
    kf_obj.embedding_status = 1
    await kf_obj.save()
    if "easyRAG" in request.app.connected_websockets:
        print(request.app.connected_websockets["easyRAG"])
        msg={"info": "处理完成","action":"splitter_end","status":1,"data":{"take_time":take_time,"splitter_time":splitter_time}}
        await request.app.connected_websockets["easyRAG"].send_text(json.dumps(msg))


@router.post("/upload")
async def upload_file(request: Request,background_tasks: BackgroundTasks,file: UploadFile = File(...)):
    # try:
        allowed_suffixes = ['txt', 'csv', 'pdf']
        file_suffix = os.path.splitext(file.filename)[1][1:]
        print(file_suffix)
        if file_suffix not in allowed_suffixes:
            return jsonReturn(info="对不起，只能上传"+"、".join(allowed_suffixes), status=0, data=[])
        form_data = await request.form()
        agent_id = form_data.get("agent_id",0)
        user_id = form_data.get("user_id", 0)
        scene_id = form_data.get("scene_id", 0)
        insertDict={"agent_id":agent_id,"user_id":user_id,"scene_id":scene_id,"file_id":0,"file_url":"","file_index":0}
        # 确保上传目录存在
        upload_dir = "./upload"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # 保存文件到本地
        file_path = os.path.join(upload_dir, file.filename)

        hash_object = hashlib.sha256()

        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024):  # 读取文件的每个块
                buffer.write(chunk)  # 写入文件
                hash_object.update(chunk)  # 更新哈希对象
        file_hash = hash_object.hexdigest()
        # fileRes=await KnowledgeFile.get(file_hash=file_hash)
        kf_objs = await KnowledgeFile.filter(file_hash=file_hash)
        if len(kf_objs) > 0:
            print(kf_objs)
            # print(kf_objs[0].id)
            os.remove(file_path)
            return jsonReturn(info="文件已经上传过", status=1, data={"filename": file.filename,"file_id": kf_objs[0].id})

        kf_obj = await KnowledgeFile.create(file_name=file.filename, file_hash=file_hash, agent_id=agent_id, scene_id=scene_id,embedding_status=0)
        print(kf_obj.id)
        print(insertDict)
        insertDict['file_id']=kf_obj.id
        background_tasks.add_task(process_text_file,insertDict,request, file_path,"")
        return jsonReturn(info="文件上传成功", status=1, data={"filename": file.filename})
    # except Exception as e:
    #     return jsonReturn(info="文件失败", status=1,data={"error": str(e)})

@router.post("/spider")
async def spider(request: Request,background_tasks: BackgroundTasks):
    data = await request.json()
    print(data)
    if "url" not in data:
        return jsonReturn(info="参数缺失 url")
    agent_id=0
    scene_id = 0
    if "agent_id" not in data:
        return jsonReturn(info="参数缺失 agent_id")
    else:
        agent_id = data["agent_id"]
    if "scene_id" not in data:
        return jsonReturn(info="参数缺失 scene_id")
    else:
        scene_id = data["scene_id"]

    url = data['url']
    response = requests.get(url)

    doc = Document(response.text)
    # 打印提取的标题
    print("Title:", doc.title())
    # 打印提取的正文内容
    print("Summary:")
    content_html = doc.summary()
    # print(content_html)
    soup = BeautifulSoup(content_html, "html.parser")
    content_text = soup.get_text().strip()
    content_text=clean_string(content_text)
    print(content_text)

    keywords = ['AccessDeny']

    # 检查字符串是否包含列表中的任何一个元素（不区分大小写）
    for keyword in keywords:
        if re.search(re.escape(keyword), doc.title(), re.IGNORECASE):
            return jsonReturn(info="改网站禁止抓取", status=0, data=[])
    if len(content_text) < 50:
        return jsonReturn(info="正文内容太少", status=0, data=[])
    if check_video_and_text_length(content_html) and len(content_text) < 150:
        return jsonReturn(info="有视频且正文内容太少", status=0, data=[])
    # print(content_text)
    if content_text=="":
        return jsonReturn(info="没有采集到数据", status=0, data=[])
    short_title = doc.short_title()
    print(f"短标题: {short_title}")
    file_hash = hashlib.sha256(content_text.encode()).hexdigest()

    insertDict = {"agent_id": agent_id, "user_id": 0, "scene_id": scene_id, "file_id": 0, "file_url": url,
                  "file_index": 0}
    kf_objs = await KnowledgeFile.filter(file_hash=file_hash)
    if len(kf_objs) > 0:
        print(kf_objs)
        return jsonReturn(info="文件已经上传过", status=1, data={"filename": doc.title(), "file_id": kf_objs[0].id})
    kf_obj = await KnowledgeFile.create(file_name=doc.title(), file_hash=file_hash, file_url=url, agent_id=agent_id,scene_id=scene_id, embedding_status=0)
    print(kf_obj.id)
    print(insertDict)
    insertDict['file_id'] = kf_obj.id
    background_tasks.add_task(process_text_file, insertDict, request, "", content_text)
    return jsonReturn(info="开始采集", status=1, data={"filename": doc.title(), "file_id": kf_obj.id})

@router.post("/search")
async def search(request: Request):
    try:
        data = await request.json()
        print(2)
        print(type(data))
        print(data)
        if isinstance(data, str):
            data = json.loads(data)
        print(data)
        if "q" not in data:
            return jsonReturn(info="参数缺失")
        q=data["q"]
        if "agent_id" in data:
            agent_id=data["agent_id"]
        if "scene_id" in data:
            scene_id=data["scene_id"]
        if "agent_id" in data:
            file_id=data["file_id"]
    except json.JSONDecodeError:
        form_data = await request.form()  # 解析表单数据
        print(2)
        print(form_data)
        q = form_data.get("q")
        if q =="":
            return jsonReturn(info="参数缺失")
        agent_id = form_data.get("agent_id")
        scene_id = form_data.get("scene_id")
        file_id = form_data.get("file_id")

    # return  {"info": "参数缺失","data":[{"content":"适合黑色地板"}]}
    # # data = await request.json()
    # # print(data)
    # if request.q == "":
    #     return jsonReturn(info="参数缺失")



    whereSql=""
    if agent_id or scene_id or file_id:
        whereSql = " WHERE"
        if agent_id != 0:
            whereSql += " agent_id="+str(agent_id)+" and"
        if scene_id != 0:
            whereSql += " scene_id="+str(scene_id)+" and"
        if file_id != 0:
            whereSql += " file_id="+str(file_id)+" and"
        whereSql=whereSql[0:-4]


    keyword= q
    print(keyword)
    embedding = request.app.vectorEncoderInstance.vectorEncode(keyword)
    # print(embedding)
    embedding_str = "ARRAY[" + ",".join(map(str, embedding)) + "]"
    try:
        print(whereSql)
        query = f"SELECT id,k_text,1-(vector_code <-> {embedding_str}::vector) AS similarity FROM public.rag_knowledge{whereSql} ORDER BY similarity DESC LIMIT 10;"
        queryset = await Tortoise.get_connection("search").execute_query(query)
        print(queryset)
        if not queryset:
            return jsonReturn(info="查询结果为空", status=1, data=[])
        res =[{"content":item["k_text"],"similarity":item["similarity"]}  for item in queryset[1]]
        return jsonReturn(info="ok", status=1, data=res)
    except Exception as e:
        print(e)
        return jsonReturn(info=str(e))

@router.post("/agents")
async def agents(request: Request):
    try:
        agent_objs = await Agent.all()
        print(agent_objs)
        if len(agent_objs)<=0:
            return jsonReturn(info="查询结果为空", status=1, data=[])
        res =[{"id":item["id"],"agent_name":item["agent_name"]}  for item in agent_objs]
        return jsonReturn(info="ok", status=1, data=res)
    except Exception as e:
        print(e)
        return jsonReturn(info=str(e))
@router.post("/agent")
async def agent(request: Request):
    try:
        data = await request.json()
        if "agent_name" not in data:
            return jsonReturn(info="参数缺失")
        agent_obj = await Agent.create(agent_name=data['agent_name'])
        return jsonReturn(info="创建智能体成功", status=1, data=agent_obj)
    except Exception as e:
        print(e)
        return jsonReturn(info=str(e))


@router.post("/files")
async def files(request: Request):
    try:
        data = await request.json()
        agent_id=0
        scene_id = 0
        if "agent_id" in data:
            agent_id = data["agent_id"]
        if "scene_id" in data:
            scene_id = data["scene_id"]
        agent_objs = await Agent.all()
        agent_list = [{"id": item.id, "agent_name": item.agent_name} for item in agent_objs]
        scene_objs = await Scene.all()
        scene_list = [{"id": item.id, "scene_name": item.scene_name} for item in scene_objs]
        if agent_id == 0:
            file_objs = []
        else:
            file_objs = await KnowledgeFile.filter(agent_id=agent_id,scene_id=scene_id).order_by('-id')
        print(file_objs)
        if len(file_objs)<=0:
            return jsonReturn(info="查询结果为空", status=1, data={"agent_list":agent_list,"scene_list":scene_list,"file_list":[]})
        res = [{"id": item.id, "file_name": item.file_name,"embedding_status": item.embedding_status} for item in file_objs]
        return jsonReturn(info="查询结果为空", status=1, data={"agent_list":agent_list,"scene_list":scene_list,"file_list":res})
    except Exception as e:
        print(e)
        return jsonReturn(info=str(e))


@router.post("/scenes")
async def scenes(request: Request):
    try:
        data = await request.json()
        if "agent_id" in data:
            scene_objs = await Scene.filter(agent_id=int(data['agent_id']))
        else:
            scene_objs = await Scene.all()
        print(scene_objs)
        if len(scene_objs)<=0:
            return jsonReturn(info="查询结果为空", status=1, data=[])
        res =[{"id":item.id,"scene_name":item.scene_name} for item in scene_objs]
        return jsonReturn(info="ok", status=1, data=res)
    except Exception as e:
        print(e)
        return jsonReturn(info=str(e))

@router.post("/scene")
async def scene(request: Request):
    try:
        data = await request.json()
        if "scene_name" not in data:
            return jsonReturn(info="参数缺失")
        agent_obj = await Scene.create(scene_name=data['scene_name'])
        return jsonReturn(info="创建场景成功", status=1, data=agent_obj)
    except Exception as e:
        print(e)
        return jsonReturn(info=str(e))
