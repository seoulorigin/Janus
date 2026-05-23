# 1. 팩트: B님의 환경(Python 3.12)에 맞춘 초경량 파이썬 3.12 공식 이미지를 뼈대로 사용합니다.
FROM python:3.12-slim

# 2. 컨테이너 내부에서 작업할 기본 폴더를 /app 으로 지정합니다.
WORKDIR /app

# 3. 우분투 환경 시스템 패키지 업데이트 (에러 방지용 필수 라이브러리 설치)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. 파이썬 라이브러리 설치 목록(requirements.txt)을 먼저 복사하고 설치합니다.
# (캐시를 활용하여 빌드 속도를 극대화하는 정석적인 방법입니다)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. B님이 작성하신 dt-engine 파이썬 소스 코드 전체를 컨테이너 안으로 복사합니다.
COPY . .

# 6. 컨테이너가 켜질 때 실행할 메인 파이썬 파일 명령입니다.
# 💡 주의: 실행하시는 메인 파이썬 파일 이름이 main.py가 아니라면 그 이름으로 수정해 주세요! (예: dt_main.py)
CMD ["python", "main.py"]