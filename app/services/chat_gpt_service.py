import os
from datetime import datetime

from fastapi import UploadFile
from openai import OpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageCompleted


UPLOAD_DIR = os.getenv("UPLOAD_DIR")
client = OpenAI()


class ChatGptService:
    @staticmethod
    async def create_assistant():
        request = {'instructions': "당신은 학습 보조입니다. 주어진 파일의 내용을 기반으로 나의 질문에 대답합니다." +
                                   " 나는 8-10세의 아동입니다. 밝고 경쾌한 어조로 대답합니다.",
                   'name': "assistant",
                   'tools': [{"type": "file_search"}],
                   'model': "gpt-4o"}

        response = client.beta.assistants.create(**request)
        return response.id

    @staticmethod
    async def create_thread():
        response = client.beta.threads.create()
        return response.id

    @staticmethod
    async def create_message(thread_id: str, message: str):
        request = {"thread_id": thread_id,
                   "role": "user",
                   "content": message}
        response = client.beta.threads.messages.create(**request)
        return response.id

    @staticmethod
    async def create_run(thread_id: str, assistant_id: str):
        request = {"thread_id": thread_id,
                   "assistant_id": assistant_id,
                   "stream": True}
        stream = client.beta.threads.runs.create(**request)

        # stream -> str
        for event in stream:
            if isinstance(event, ThreadMessageCompleted):
                return event.data.content[0].text.value

    @staticmethod
    async def create_file(file: UploadFile):
        filename = "{}_{}".format(datetime.now().strftime("%y%m%d%H%M%S"), file.filename)

        content = await file.read()
        with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
            fp.write(content)

        request = {"file": open(os.path.join(UPLOAD_DIR, filename), "rb"),
                   "purpose": "assistants"}
        response = client.files.create(**request)
        return response.id

    @staticmethod
    async def create_vector_store():
        response = client.beta.vector_stores.create()
        return response.id

    @staticmethod
    async def attach_vector_store_to_thread(thread_id: str, vector_store_id: str):
        request = {
            "thread_id": thread_id,
            "tool_resources": {"file_search": {"vector_store_ids": [vector_store_id]}}
        }

        response = client.beta.threads.update(**request)
        return response.id

    @staticmethod
    async def attach_file_to_vector_store(file_id: str, vector_store_id: str):
        request = {"vector_store_id": vector_store_id,
                   "file_id": file_id}
        response = client.beta.vector_stores.files.create(**request)
        print(response)
        return response.id

    @staticmethod
    async def delete_thread(thread_id: str):
        response = client.beta.threads.delete(thread_id)
        return response.id

    @staticmethod
    async def delete_vector_store(vector_store_id: str):
        response = client.beta.vector_stores.delete(vector_store_id)
        return response.id