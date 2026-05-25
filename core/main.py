import os
import sys
import joblib
from kafka import KafkaConsumer
import time
from kafka.errors import NoBrokersAvailable
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
                auto_offset_reset='latest',
            )
            print("카프카 연결 성공!", flush=True)
            break
        except NoBrokersAvailable:
            print(f"카프카 대기 중... ({i+1}/{max_retries})", flush=True)
            time.sleep(10)

    for message in consumer:
        try:
            raw_text = message.value.decode('utf-8').strip()
            print(f"[DEBUG] 받은 원본 데이터: {repr(raw_text)}", flush=True)

            tokens = raw_text.split()
            syscall_list = []
            for t in tokens:
                t = t.strip().lstrip('>')
                if t.lstrip('-').isdigit():
                    syscall_list.append(int(t))

            print(f"[DEBUG] 파싱된 숫자 리스트: {syscall_list}", flush=True)

            if len(syscall_list) < 5:
                continue

            input_features = make_dt_5gram(syscall_list)

            if input_features is None or len(input_features) == 0:
                continue

            prediction = model.predict(input_features)[0]
            probability = model.predict_proba(input_features)[0]

            if prediction in [0, 1]:
                print(f"[CRITICAL] 크립토재킹 탐지! (class={prediction}, 확률: {max(probability)*100:.2f}%) | 입력: {syscall_list[:10]}", flush=True)
            else:
                print(f"[정상] class={prediction} | 입력: {syscall_list[:10]}", flush=True)

        except Exception as eval_error:
            print(f"[WARN] 데이터 전처리 및 추론 중 에러 발생: {eval_error}", file=sys.stderr, flush=True)

if __name__ == '__main__':
    main()
