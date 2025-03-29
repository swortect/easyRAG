from tortoise import Model, fields
from tortoise_vector.field import VectorField


# class MyModel(Model):
#     id = fields.IntField(pk=True)
#     embedding = VectorField(vector_size=1536)  # 假设使用 OpenAI 的 1536 维向量
#     name = fields.CharField(max_length=100, null=True, default="default_agent_name")
#
#     class Meta:
#         table = "my_custom_table_name"  # 指定表名
#         schema = "my_custom_schema"     # 指定 schema


class Knowledge(Model):
    id = fields.IntField(pk=True)
    agent_id = fields.IntField(null=True,default=0)
    user_id = fields.IntField(null=True,default=0)
    scene_id = fields.IntField(null=True,default=0)
    file_id = fields.IntField(null=True,default=0)
    file_index = fields.IntField(null=True,default=0)
    k_text = fields.CharField(max_length=500, null=True)
    vector_code = VectorField(vector_size=1024, null=True)
    embedding_model = fields.CharField(max_length=100, null=True, default="bge-large-zh-v1.5")
    class Meta:
        table = "rag_knowledge"
        # schema = "agents"
    def __str__(self):
        return self.k_text

    def to_dict(self):  # 这个方法自定义的时候使用
        data = {i: getattr(self, i) for i in self.__dict__ if not i.startswith('_')}
        return data


class KnowledgeFile(Model):
    id = fields.IntField(pk=True)
    agent_id = fields.IntField(null=True,default=0)
    user_id = fields.IntField(null=True,default=0)
    scene_id = fields.IntField(null=True, default=0)
    file_name = fields.CharField(max_length=100, null=True)
    file_url = fields.CharField(max_length=200, null=True)
    file_hash = fields.CharField(max_length=100, null=True)
    embedding_status = fields.IntField(null=True, default=0)
    file_name_vector_code = VectorField(vector_size=1024, null=True)
    embedding_model = fields.CharField(max_length=100, null=True, default="bge-large-zh-v1.5")
    class Meta:
        table = "rag_knowledge_file"
        # schema = "agents"
    def __str__(self):
        return self.file_name

    def to_dict(self):  # 这个方法自定义的时候使用
        data = {i: getattr(self, i) for i in self.__dict__ if not i.startswith('_')}
        return data
class Agent(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField(null=True, default=0)
    embedding = VectorField(vector_size=1536)  # 假设使用 OpenAI 的 1536 维向量
    agent_name = fields.CharField(max_length=100)
    class Meta:
        table = "rag_agent"
        # schema = "agents"
    def __str__(self):
        return self.agent_name

    def to_dict(self):  # 这个方法自定义的时候使用
        data = {i: getattr(self, i) for i in self.__dict__ if not i.startswith('_')}
        return data
class Scene(Model):
    id = fields.IntField(pk=True)
    agent_id = fields.IntField(null=True, default=0)
    user_id = fields.IntField(null=True, default=0)
    scene_name = fields.CharField(max_length=100)
    class Meta:
        table = "rag_scene"
        # schema = "agents"
    def __str__(self):
        return self.scene_name

    def to_dict(self):  # 这个方法自定义的时候使用
        data = {i: getattr(self, i) for i in self.__dict__ if not i.startswith('_')}
        return data