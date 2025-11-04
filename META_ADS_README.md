# 📢 Meta 광고 자동화 도구

Meta(Facebook/Instagram) 광고를 자동으로 생성하고 관리하는 Streamlit 기반 웹 애플리케이션입니다.

## ✨ 주요 기능

### 1. 캠페인 관리
- ✅ 기존 캠페인 조회 및 필터링
- ✅ 새 캠페인 생성
- ✅ 캠페인별 광고 세트 조회

### 2. 광고 세트 관리
- ✅ 기존 광고 세트 선택
- ✅ 새 광고 세트 생성
- ✅ 예산 설정 (일일/총 예산)
- ✅ 최적화 목표 설정

### 3. 광고 생성
- ✅ 이미지 광고 자동 생성
- ✅ 비디오 광고 자동 생성
- ✅ 크리에이티브 자동 업로드
- ✅ CTA 버튼 설정

### 4. 타겟팅 설정
- ✅ 국가 타겟팅
- ✅ 연령대 설정
- ✅ 성별 타겟팅
- ✅ 관심사 타겟팅
- ✅ 언어 설정
- ✅ 타겟팅 템플릿 저장

### 5. 일괄 업로드
- ✅ 여러 크리에이티브 동시 업로드
- ✅ 광고 자동 생성
- ✅ 진행 상황 실시간 표시

## 🚀 설치 방법

### 1. 필요한 패키지 설치

```bash
pip install -r requirements_meta_ads.txt
```

### 2. Meta 개발자 앱 설정

#### 2.1 Meta 개발자 계정 생성
1. https://developers.facebook.com/ 방문
2. 계정 생성 또는 로그인

#### 2.2 앱 생성
1. "내 앱" → "앱 만들기"
2. 앱 유형 선택: "비즈니스"
3. 앱 정보 입력
4. 앱 생성 완료

#### 2.3 Marketing API 추가
1. 앱 대시보드에서 "제품 추가"
2. "Marketing API" 선택 및 설정

#### 2.4 앱 정보 확인
- **App ID**: 앱 대시보드 상단에 표시
- **App Secret**: 앱 설정 → 기본 설정

#### 2.5 액세스 토큰 생성

**방법 1: 임시 토큰 (테스트용)**
1. 도구 → Graph API 탐색기
2. 권한 추가:
   - `ads_management`
   - `ads_read`
   - `business_management`
3. "액세스 토큰 생성"

**방법 2: 장기 토큰 (프로덕션용)**
```bash
curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token" \
  -d "grant_type=fb_exchange_token" \
  -d "client_id=YOUR_APP_ID" \
  -d "client_secret=YOUR_APP_SECRET" \
  -d "fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

#### 2.6 광고 계정 ID 확인
1. Meta 광고 관리자: https://business.facebook.com/adsmanager/
2. 계정 설정에서 광고 계정 ID 확인
3. 형식: `act_123456789` 또는 `123456789`

#### 2.7 Facebook 페이지 ID 확인
1. Facebook 페이지 방문
2. 페이지 정보 → "페이지 ID" 확인
3. 또는 URL에서 숫자 ID 확인

## 📖 사용 방법

### 1. 애플리케이션 실행

```bash
streamlit run meta_ads_automation.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 접속 가능합니다.

### 2. API 설정

왼쪽 사이드바에 다음 정보 입력:
- **App ID**: Meta 앱 ID
- **App Secret**: Meta 앱 시크릿
- **Access Token**: 생성한 액세스 토큰
- **광고 계정 ID**: act_xxxxx 형식

### 3. 캠페인 조회

"📊 캠페인 조회" 탭에서:
1. 상태 필터 선택 (ACTIVE, PAUSED 등)
2. 캠페인 목록 확인
3. 캠페인 선택하여 광고 세트 조회

### 4. 광고 생성

"🎨 광고 생성" 탭에서:

#### 4.1 캠페인 선택/생성
- **기존 캠페인**: 드롭다운에서 선택
- **새 캠페인**: 캠페인명과 목표 입력 후 생성

#### 4.2 광고 세트 선택/생성
- **기존 세트**: 드롭다운에서 선택
- **새 세트**: 다음 정보 입력
  - 광고 세트명
  - 일일 예산 (USD)
  - 최적화 목표
  - 타겟팅 (국가, 연령)

#### 4.3 광고 크리에이티브 생성
1. 광고명 입력
2. 광고 메시지 작성
3. 랜딩 페이지 URL 입력
4. Facebook 페이지 ID 입력
5. 크리에이티브 타입 선택 (이미지/비디오)
6. CTA 버튼 선택
7. 파일 업로드
8. "광고 생성" 버튼 클릭

### 5. 타겟팅 템플릿

"⚙️ 타겟팅 설정" 탭에서:
1. 템플릿명 입력
2. 타겟팅 조건 설정:
   - 국가
   - 연령대
   - 성별
   - 언어
   - 관심사 ID
3. "템플릿 저장" 클릭
4. 저장된 템플릿은 나중에 재사용 가능

### 6. 일괄 업로드

"📤 자동 업로드" 탭에서:
1. 대상 캠페인 선택
2. 대상 광고 세트 선택
3. 공통 설정 입력:
   - 광고 메시지 템플릿
   - 랜딩 페이지 URL
   - Facebook 페이지 ID
   - CTA 버튼
4. 여러 이미지/비디오 선택
5. "일괄 광고 생성" 클릭
6. 진행 상황 확인

## 🎯 캠페인 목표 (Objective) 설명

| 목표 | 설명 | 사용 사례 |
|------|------|----------|
| `OUTCOME_TRAFFIC` | 트래픽 증가 | 웹사이트 방문자 유도 |
| `OUTCOME_LEADS` | 리드 생성 | 연락처 수집, 가입 유도 |
| `OUTCOME_SALES` | 판매 전환 | 온라인 구매 유도 |
| `OUTCOME_AWARENESS` | 인지도 증대 | 브랜드 노출 극대화 |
| `OUTCOME_ENGAGEMENT` | 참여 유도 | 좋아요, 댓글, 공유 증가 |

## 📊 최적화 목표 설명

| 목표 | 설명 | 과금 방식 |
|------|------|----------|
| `REACH` | 도달 범위 | 도달한 사람 수 기준 |
| `IMPRESSIONS` | 노출 수 | 광고 표시 횟수 기준 |
| `LINK_CLICKS` | 링크 클릭 | 클릭당 과금 |
| `CONVERSIONS` | 전환 | 전환 발생 시 과금 |

## 🎨 CTA 버튼 종류

| 버튼 | 한글 | 용도 |
|------|------|------|
| `LEARN_MORE` | 자세히 알아보기 | 정보 제공 |
| `SHOP_NOW` | 지금 쇼핑하기 | 이커머스 |
| `SIGN_UP` | 가입하기 | 회원 가입 |
| `DOWNLOAD` | 다운로드 | 앱/파일 다운로드 |
| `CONTACT_US` | 문의하기 | 고객 문의 |

## 🔍 관심사 ID 찾기

### 방법 1: Meta Ads Manager 사용
1. 광고 관리자에서 새 광고 세트 생성
2. 타겟팅 → 관심사 검색
3. 관심사 선택 시 URL에서 ID 확인

### 방법 2: Graph API 탐색기 사용
```
GET https://graph.facebook.com/v18.0/search
  ?type=adinterest
  &q=영화
  &access_token=YOUR_TOKEN
```

예시 응답:
```json
{
  "data": [
    {
      "id": "6003139266461",
      "name": "Movies",
      "audience_size": 1234567890
    }
  ]
}
```

## 🌍 주요 국가 코드

| 코드 | 국가 | 코드 | 국가 |
|------|------|------|------|
| `KR` | 대한민국 | `US` | 미국 |
| `JP` | 일본 | `CN` | 중국 |
| `TW` | 대만 | `HK` | 홍콩 |
| `SG` | 싱가포르 | `VN` | 베트남 |

## 🗣️ 언어 코드

| 코드 | 언어 |
|------|------|
| `6` | 한국어 (Korean) |
| `24` | 영어 (English) |

## 💰 예산 설정 팁

### 일일 예산 추천
- **테스트**: $5-10/일
- **소규모**: $20-50/일
- **중규모**: $100-500/일
- **대규모**: $1,000+/일

### 예산 계산
- API는 센트 단위 사용
- $10 = 1,000센트
- 코드에서 자동 변환 처리

## ⚠️ 주의사항

### 1. 광고 승인
- 생성된 광고는 Meta의 검토를 거쳐야 합니다
- 보통 24시간 이내 승인/거부 결정
- 정책 위반 시 광고 계정 제재 가능

### 2. 광고 상태
- 광고는 기본적으로 **PAUSED** 상태로 생성됩니다
- 검토 후 Meta Ads Manager에서 수동으로 활성화하세요
- 또는 코드에서 `status='ACTIVE'`로 설정 가능

### 3. 크리에이티브 규격

**이미지**
- 권장 크기: 1200 x 628px
- 최소 크기: 600 x 314px
- 파일 형식: JPG, PNG
- 최대 크기: 30MB
- 텍스트: 이미지의 20% 미만 권장

**비디오**
- 권장 크기: 1280 x 720px 이상
- 파일 형식: MP4, MOV
- 최대 크기: 4GB
- 길이: 1초 ~ 240분
- 비율: 9:16, 1:1, 4:5 권장

### 4. 토큰 보안
- 액세스 토큰은 절대 공개하지 마세요
- 환경 변수 사용 권장:
  ```bash
  export META_ACCESS_TOKEN="your_token"
  export META_APP_ID="your_app_id"
  export META_APP_SECRET="your_app_secret"
  export META_AD_ACCOUNT_ID="act_123456"
  ```

### 5. API 제한
- Meta API는 요청 수 제한이 있습니다
- 대량 작업 시 적절한 딜레이 추가 권장
- 에러 발생 시 재시도 로직 구현 필요

## 🐛 문제 해결

### "Invalid OAuth access token" 오류
- 토큰 만료 확인
- 새 토큰 생성 필요
- 권한 설정 확인

### "Insufficient permissions" 오류
- 앱에 Marketing API 권한 부여 확인
- 토큰 생성 시 필요한 권한 포함 확인
- 광고 계정 접근 권한 확인

### "Ad account not found" 오류
- 광고 계정 ID 형식 확인 (act_xxxxx)
- 계정 접근 권한 확인

### 크리에이티브 업로드 실패
- 파일 크기 확인
- 파일 형식 확인
- 네트워크 연결 확인

## 📚 추가 리소스

- [Meta Marketing API 문서](https://developers.facebook.com/docs/marketing-apis)
- [Facebook Business SDK (Python)](https://github.com/facebook/facebook-python-business-sdk)
- [Meta 광고 정책](https://www.facebook.com/policies/ads/)
- [광고 사양 가이드](https://www.facebook.com/business/ads-guide)

## 🔄 업데이트 계획

- [ ] 캐러셀 광고 지원
- [ ] 광고 성과 대시보드
- [ ] A/B 테스트 자동화
- [ ] 예산 최적화 알고리즘
- [ ] 스케줄링 기능
- [ ] 커스텀 오디언스 관리

## 📧 문의

문제가 발생하거나 기능 제안이 있으시면 이슈를 등록해주세요.

---

**⚖️ 면책 조항**: 이 도구는 Meta Marketing API를 활용한 자동화 도구입니다. 광고 운영 결과에 대한 책임은 사용자에게 있으며, Meta의 광고 정책을 준수해야 합니다.
