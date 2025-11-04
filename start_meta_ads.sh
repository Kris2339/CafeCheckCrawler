#!/bin/bash

# Meta Ads Automation - Quick Start Script
# 메타 광고 자동화 도구 실행 스크립트

echo "🚀 Meta 광고 자동화 도구 시작"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 가상 환경을 생성합니다..."
    python3 -m venv venv
    echo "✅ 가상 환경 생성 완료"
    echo ""
fi

# Activate virtual environment
echo "🔧 가상 환경 활성화..."
source venv/bin/activate

# Install/Update requirements
echo "📥 필요한 패키지 설치 중..."
pip install -r requirements_meta_ads.txt --quiet
echo "✅ 패키지 설치 완료"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다"
    echo "   .env.example을 참고하여 .env 파일을 생성해주세요"
    echo ""
fi

# Start Streamlit
echo "🌐 Streamlit 서버 시작..."
echo "   브라우저에서 http://localhost:8501 로 접속하세요"
echo ""

streamlit run meta_ads_automation.py
