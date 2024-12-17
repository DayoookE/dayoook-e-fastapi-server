import os
import uuid
from datetime import datetime
from io import BytesIO
from tempfile import NamedTemporaryFile

from fastapi import UploadFile
from openai import OpenAI
from openai.types.beta.assistant_stream_event import ThreadMessageCompleted


UPLOAD_DIR = os.getenv("UPLOAD_DIR")
client = OpenAI()


class ChatGptService:
    @staticmethod
    async def create_chat_assistant():
        request = {'instructions': "당신은 학습 보조입니다. 주어진 파일의 내용을 기반으로 나의 질문에 대답합니다." +
                                   " 나는 8-10세의 아동입니다. 밝고 경쾌한 어조로 대답합니다.",
                   'name': "assistant",
                   'tools': [{"type": "file_search"}],
                   'model': "gpt-4o"}

        response = client.beta.assistants.create(**request)
        return response.id

    @staticmethod
    async def create_review_assistant():
        request = {'instructions': "당신은 학습 보조입니다. 주어진 대화문을 기반으로 복습 자료를 생성합니다." +
                                   " 나는 8-10세의 아동입니다. 복습 자료의 분량은 공백 포함 700자 이내입니다." +
                                   " **마크다운을 이용하여** 체계적으로 정리합니다. 파일 출처는 표시하지 않습니다.",
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
    async def create_file(bytes : BytesIO):
        request = {"file": bytes,
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