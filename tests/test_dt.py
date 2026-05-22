import joblib
from core.preprocess import make_dt_5gram

print("1. Colab에서 학습한 DT 모델 로딩 중...")
dt_model = joblib.load('/data/janus/models/cryptojacking_dt_model.joblib')

# 2. 가상의 시스템 콜 데이터 준비 (Tetragon이 잡아낸 데이터라고 가정)
# 총 12개의 정수입니다.
mock_syscalls = [
    186, 14, 14, 3, 13,   # 1번 그룹 (5개)
    59, 158, 218, 12, 12, # 2번 그룹 (5개)
    1, 2                  # 5개가 안 되므로 전처리 과정에서 자동으로 잘려나감
]
print(f"2. 입력된 원본 시스템 콜 개수: {len(mock_syscalls)}개")

# 3. 전처리 수행 (우리가 만든 모듈 사용!)
features = make_dt_5gram(mock_syscalls)
print(f"3. 전처리 완료! 모델에 들어갈 데이터 형태(Shape): {features.shape}")
print(f"   변환된 행렬 데이터:\n{features}")

# 4. 모델 추론
print("\n4. DT 모델 실시간 추론 결과:")
predictions = dt_model.predict(features)

for i, pred in enumerate(predictions):
    # 일반적으로 악성을 1, 정상을 0으로 라벨링했다고 가정합니다.
    label = "🚨 악성(채굴 의심)" if pred == 1 else "✅ 정상"
    print(f" - {i+1}번째 5-gram {features[i]} ➔ 판결: {label}")