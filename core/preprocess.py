import numpy as np

def make_dt_5gram(syscall_list):
    """
    의사결정나무(DT)용: Non-overlapping 5-gram 배열 생성
    - 입력: 1차원 정수 리스트 (예: [186, 14, 14, 3, 13, 59, ...])
    - 출력: 5개씩 묶인 2차원 numpy 배열
    - 특징: 5개 단위로 떨어지지 않고 남는 자투리 데이터는 과감히 버림
    """
    dt_features = []
    
    # 5칸씩 점프하며 중복 없이 슬라이싱 (Non-overlapping)
    for i in range(0, len(syscall_list) - 4, 5):
        frame = syscall_list[i:i+5]
        dt_features.append(frame)
        
    return np.array(dt_features) # 모델이 요구하는 (N, 5) 형태의 행렬로 반환