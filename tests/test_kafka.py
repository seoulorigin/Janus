import json
import sys
from kafka import KafkaProducer, KafkaConsumer

KAFKA_BROKER = 'localhost:9092'

try:
    print("1. Kafka Producer(송신자) 연결 시도 중...")
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks=1
    )
    # 가짜 커널 로그 데이터를 sys-logs 토픽으로 전송
    test_data = {"pod_name": "test-pod-1", "syscall_id": 186}
    producer.send('sys-logs', test_data)
    producer.flush()
    print("✅ sys-logs 토픽으로 테스트 데이터 전송 성공!")

    print("\n2. Kafka Consumer(수신자) 연결 및 데이터 확인 중...")
    consumer = KafkaConsumer(
        'sys-logs',
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=4000 # 데이터가 없으면 4초 뒤 자동 종료
    )

    data_received = False
    for message in consumer:
        print(f"📥 수신된 실시간 데이터: {message.value}")
        data_received = True
        break # 하나만 확인하고 루프 탈출
        
    if data_received:
        print("\n✅ [대성공] Kafka 양방향 통신망 개통 완벽 검증 완료!")
    else:
        print("\n❌ [실패] 카프카 서버는 켜졌으나 데이터를 받지 못했습니다.")

except Exception as e:
    print(f"\n❌ [에러 발생] 카프카 연결 실패: {e}")
    sys.exit(1)