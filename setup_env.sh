#!/bin/bash
set -e # 에러 발생 시 즉시 중단

echo -e "\033[1;34m[1/6] 시스템 업데이트 및 필수 패키지 설치 중...\033[0m"
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y curl gnupg lsb-release python3-pip python3-venv git

echo -e "\033[1;34m[2/6] Docker 엔진 설치 및 저장소 등록 중...\033[0m"
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo -e "\033[1;34m[3/6] Kubectl (쿠버네티스 CLI) 설치 중...\033[0m"
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

echo -e "\033[1;34m[4/6] Minikube 설치 중...\033[0m"
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64

echo -e "\033[1;34m[5/6] Helm v3 설치 중...\033[0m"
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

echo -e "\033[1;34m[6/6] Docker 권한 설정 중...\033[0m"
sudo usermod -aG docker $USER

echo -e "\033[1;34m[1/4] 파이썬 venv 가상환경 생성 중...\033[0m"
python3 -m venv venv

echo -e "\033[1;34m[2/4] pip 클라이언트 최신화 중...\033[0m"
./venv/bin/pip install --upgrade pip

echo -e "\033[1;34m[3/4] 리소스 절감형 CPU 전용 ML 패키지 및 Kafka 라이브러리 설치 중...\033[0m"
./venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
./venv/bin/pip install numpy scikit-learn==1.6.1 joblib kafka-python-ng

echo -e "\033[1;34m[4/4] .bashrc에 '폴더 진입 시 가상환경 자동 켜기/끄기' 매크로 심는 중...\033[0m"
# 이미 등록되어 있는지 확인 후, 없을 때만 중복되지 않게 주입합니다.
if ! grep -q "# \[Python venv 자동 켜기/끄기 매크로\]" ~/.bashrc; then
cat << 'BASHRC' >> ~/.bashrc

# ==========================================
# [Python venv 자동 켜기/끄기 매크로]
# ==========================================
cd() {
    builtin cd "$@"
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        echo -e "\033[1;32m[가상환경 자동 활성화]\033[0m"
    elif [[ -n "$VIRTUAL_ENV" && ! "$PWD" =~ $(dirname "$VIRTUAL_ENV") ]]; then
        deactivate
        echo -e "\033[1;31m[가상환경 자동 비활성화]\033[0m"
    fi
}
BASHRC
fi

echo -e "\n\033[1;32m[✔] 가상환경 구축 및 모든 도구가 성공적으로 설치되었습니다!\033[0m"
echo -e "\033[1;33m실행을 마무리하기 위해 아래 명령어를 터미널에 입력해 주세요:\033[0m"
echo -e "--> \033[1;36msource ~/.bashrc\033[0m \n"
echo -e "--> \033[1;36mnewgrp docker\033[0m \n"