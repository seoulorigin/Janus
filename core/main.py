import os
import sys
import json
import joblib
from kafka import KafkaConsumer

import time
from kafka.errors import NoBrokersAvailable

# 💡 [핵심 팩트] B님이 미리 만들어두신 전처리 모듈과 함수를 임포트합니다.
from preprocess import make_dt_5gram

def main():
    print("[Janus DT Engine] 추론 서비스 기동 시작...", flush=True)

    model_path = '/app/models/cryptojacking_dt_model.joblib'
    
    if not os.path.exists(model_path):
        print(f"[ERROR] 모델 파일을 찾을 수 없습니다: {model_path}", file=sys.stderr, flush=True)
        sys.exit(1)

    try:
        model = joblib.load(model_path)
        print(f"[Janus DT Engine] AI 모델 로드 완료 (타입: {type(model).__name__})", flush=True)
    except Exception as e:
        print(f"[ERROR] 모델 로드 실패: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

    KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "janus-app-kafka:9092")
    TOPIC_NAME = os.getenv("KAFKA_TOPIC", "tetragon-logs")

    max_retries = 10
    for i in range(max_retries):
        try:
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=[KAFKA_BROKER],
                # ... 나머지 설정 ...
            )
            print("카프카 연결 성공!", flush=True)
            break
        except NoBrokersAvailable:
            print(f"카프카 대기 중... ({i+1}/{max_retries})", flush=True)
            time.sleep(10)

    for message in consumer:
        log_data = message.value
        
        try:
            # 1. 💡 B님의 전처리 함수에 카프카 Raw 로그를 통째로 던집니다.
            # 이 함수는 내부에서 연산을 거친 뒤, 모델이 먹을 수 있는 형태(DataFrame 또는 2D Array)로 반환해야 합니다.
            input_features = make_dt_5gram(log_data)
            
            # 만약 전처리 로직에서 필터링되어 분석할 필요가 없는 로그라면 None을 반환하도록 설계할 수도 있습니다.
            if input_features is None:
                continue

            # 2. 전처리된 깔끔한 데이터를 AI 모델에 찔러 넣습니다.
            prediction = model.predict(input_features)[0]
            probability = model.predict_proba(input_features)[0]

            # 3. 결과 관제 
            if prediction == 1:
                print(f"[🚨 CRITICAL] 크립토재킹 탐지! (확률: {probability[1]*100:.2f}%) | 타겟 데이터: {log_data}", flush=True)
            else:
                pass # 정상 로그는 서버 부하 방지를 위해 콘솔 출력을 생략 (필요시 활성화)

        except Exception as eval_error:
            print(f"[WARN] 데이터 전처리 및 추론 중 에러 발생: {eval_error}", file=sys.stderr, flush=True)

if __name__ == '__main__':
    main()