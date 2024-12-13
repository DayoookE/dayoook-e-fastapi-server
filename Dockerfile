FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-runtime

WORKDIR /server

# apt-get과 pip install을 하나의 RUN으로 합치고 캐시 정리
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends && \
    apt-get install net-tools -y &&  \
    apt-get install ffmpeg libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt를 먼저 복사해서 레이어 캐싱 활용
COPY container/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 파일들 복사
COPY container .

# 실행 권한 설정
RUN chmod +x run.py

EXPOSE 6262

CMD ["python", "run.py"]

# 도커 컨테이너 실행 시 다음 명령어 사용
# docker run -v $(pwd)/container:/server --gpus all --name [CONTAINER_NAME] -p 6262:6262 [IMAGE_NAME:IMAGE_TAG]