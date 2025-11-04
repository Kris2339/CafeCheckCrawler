"""
Meta Ads Automation Tool
========================
메타(Facebook/Instagram) 광고를 자동으로 생성하고 관리하는 도구

주요 기능:
- 기존 캠페인 및 광고 세트 조회
- 크리에이티브(이미지/비디오) 업로드
- 자동 광고 생성 및 라이브
- 타겟팅 및 예산 설정
"""

import streamlit as st
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.advideo import AdVideo
import json
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional
import pandas as pd


class MetaAdsAutomation:
    """메타 광고 자동화 클래스"""

    def __init__(self, access_token: str, ad_account_id: str, app_id: str, app_secret: str):
        """
        초기화

        Args:
            access_token: Meta API 액세스 토큰
            ad_account_id: 광고 계정 ID (act_xxxxx 형식)
            app_id: Meta 앱 ID
            app_secret: Meta 앱 시크릿
        """
        # API 초기화
        FacebookAdsApi.init(app_id, app_secret, access_token)
        self.api = FacebookAdsApi.get_default_api()

        # 광고 계정 ID 설정
        if not ad_account_id.startswith('act_'):
            ad_account_id = f'act_{ad_account_id}'
        self.ad_account_id = ad_account_id
        self.ad_account = AdAccount(ad_account_id)

    def get_campaigns(self, status_filter: Optional[List[str]] = None) -> pd.DataFrame:
        """
        캠페인 목록 조회

        Args:
            status_filter: 상태 필터 (예: ['ACTIVE', 'PAUSED'])

        Returns:
            캠페인 목록 DataFrame
        """
        params = {
            'fields': [
                'id',
                'name',
                'status',
                'objective',
                'daily_budget',
                'lifetime_budget',
                'created_time',
                'updated_time'
            ]
        }

        if status_filter:
            params['filtering'] = [{'field': 'status', 'operator': 'IN', 'value': status_filter}]

        campaigns = self.ad_account.get_campaigns(params=params)

        campaign_list = []
        for campaign in campaigns:
            campaign_list.append({
                'ID': campaign.get('id'),
                '캠페인명': campaign.get('name'),
                '상태': campaign.get('status'),
                '목표': campaign.get('objective'),
                '일일예산': campaign.get('daily_budget', 'N/A'),
                '총예산': campaign.get('lifetime_budget', 'N/A'),
                '생성일': campaign.get('created_time'),
            })

        return pd.DataFrame(campaign_list)

    def get_adsets(self, campaign_id: str) -> pd.DataFrame:
        """
        특정 캠페인의 광고 세트 목록 조회

        Args:
            campaign_id: 캠페인 ID

        Returns:
            광고 세트 목록 DataFrame
        """
        campaign = Campaign(campaign_id)

        params = {
            'fields': [
                'id',
                'name',
                'status',
                'daily_budget',
                'lifetime_budget',
                'start_time',
                'end_time',
                'targeting',
                'optimization_goal',
                'billing_event'
            ]
        }

        adsets = campaign.get_ad_sets(params=params)

        adset_list = []
        for adset in adsets:
            targeting = adset.get('targeting', {})
            adset_list.append({
                'ID': adset.get('id'),
                '광고세트명': adset.get('name'),
                '상태': adset.get('status'),
                '일일예산': adset.get('daily_budget', 'N/A'),
                '총예산': adset.get('lifetime_budget', 'N/A'),
                '시작일': adset.get('start_time'),
                '종료일': adset.get('end_time', 'N/A'),
                '최적화목표': adset.get('optimization_goal'),
            })

        return pd.DataFrame(adset_list)

    def upload_image(self, image_path: str, image_name: Optional[str] = None) -> str:
        """
        이미지 업로드

        Args:
            image_path: 이미지 파일 경로
            image_name: 이미지 이름 (선택사항)

        Returns:
            업로드된 이미지 해시
        """
        if not image_name:
            image_name = os.path.basename(image_path)

        image = AdImage(parent_id=self.ad_account_id)
        image[AdImage.Field.filename] = image_path
        image.remote_create()

        return image[AdImage.Field.hash]

    def upload_video(self, video_path: str, video_name: Optional[str] = None) -> str:
        """
        비디오 업로드

        Args:
            video_path: 비디오 파일 경로
            video_name: 비디오 이름 (선택사항)

        Returns:
            업로드된 비디오 ID
        """
        if not video_name:
            video_name = os.path.basename(video_path)

        video = AdVideo(parent_id=self.ad_account_id)
        video[AdVideo.Field.filepath] = video_path
        video.remote_create()

        return video['id']

    def create_campaign(
        self,
        campaign_name: str,
        objective: str,
        status: str = 'PAUSED',
        special_ad_categories: Optional[List[str]] = None
    ) -> str:
        """
        새 캠페인 생성

        Args:
            campaign_name: 캠페인 이름
            objective: 캠페인 목표 (예: 'OUTCOME_TRAFFIC', 'OUTCOME_LEADS', 'OUTCOME_SALES')
            status: 초기 상태 (ACTIVE, PAUSED)
            special_ad_categories: 특수 광고 카테고리 (예: ['NONE'])

        Returns:
            생성된 캠페인 ID
        """
        params = {
            Campaign.Field.name: campaign_name,
            Campaign.Field.objective: objective,
            Campaign.Field.status: status,
            Campaign.Field.special_ad_categories: special_ad_categories or ['NONE']
        }

        campaign = self.ad_account.create_campaign(params=params)
        return campaign['id']

    def create_adset(
        self,
        campaign_id: str,
        adset_name: str,
        daily_budget: int,
        targeting: Dict,
        billing_event: str = 'IMPRESSIONS',
        optimization_goal: str = 'REACH',
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: str = 'PAUSED'
    ) -> str:
        """
        새 광고 세트 생성

        Args:
            campaign_id: 캠페인 ID
            adset_name: 광고 세트 이름
            daily_budget: 일일 예산 (센트 단위, 예: 10000 = $100)
            targeting: 타겟팅 설정
            billing_event: 과금 이벤트
            optimization_goal: 최적화 목표
            start_time: 시작 시간
            end_time: 종료 시간
            status: 초기 상태

        Returns:
            생성된 광고 세트 ID
        """
        if not start_time:
            start_time = datetime.now()

        params = {
            AdSet.Field.name: adset_name,
            AdSet.Field.campaign_id: campaign_id,
            AdSet.Field.daily_budget: daily_budget,
            AdSet.Field.billing_event: billing_event,
            AdSet.Field.optimization_goal: optimization_goal,
            AdSet.Field.targeting: targeting,
            AdSet.Field.status: status,
            AdSet.Field.start_time: start_time.isoformat(),
        }

        if end_time:
            params[AdSet.Field.end_time] = end_time.isoformat()

        adset = self.ad_account.create_ad_set(params=params)
        return adset['id']

    def create_image_ad(
        self,
        adset_id: str,
        ad_name: str,
        image_hash: str,
        message: str,
        link: str,
        page_id: str,
        instagram_actor_id: Optional[str] = None,
        call_to_action: str = 'LEARN_MORE',
        status: str = 'PAUSED'
    ) -> str:
        """
        이미지 광고 생성

        Args:
            adset_id: 광고 세트 ID
            ad_name: 광고 이름
            image_hash: 업로드된 이미지 해시
            message: 광고 메시지
            link: 랜딩 페이지 URL
            page_id: Facebook 페이지 ID
            instagram_actor_id: Instagram 계정 ID (선택사항)
            call_to_action: CTA 버튼 타입
            status: 초기 상태

        Returns:
            생성된 광고 ID
        """
        # 크리에이티브 생성
        link_data = {
            'message': message,
            'link': link,
            'image_hash': image_hash,
            'call_to_action': {
                'type': call_to_action,
                'value': {
                    'link': link
                }
            }
        }

        creative_params = {
            AdCreative.Field.name: f'{ad_name} - Creative',
            AdCreative.Field.object_story_spec: {
                'page_id': page_id,
                'link_data': link_data
            }
        }

        if instagram_actor_id:
            creative_params[AdCreative.Field.object_story_spec]['instagram_actor_id'] = instagram_actor_id

        creative = self.ad_account.create_ad_creative(params=creative_params)

        # 광고 생성
        ad_params = {
            Ad.Field.name: ad_name,
            Ad.Field.adset_id: adset_id,
            Ad.Field.creative: {'creative_id': creative['id']},
            Ad.Field.status: status
        }

        ad = self.ad_account.create_ad(params=ad_params)
        return ad['id']

    def create_video_ad(
        self,
        adset_id: str,
        ad_name: str,
        video_id: str,
        message: str,
        link: str,
        page_id: str,
        instagram_actor_id: Optional[str] = None,
        call_to_action: str = 'LEARN_MORE',
        status: str = 'PAUSED'
    ) -> str:
        """
        비디오 광고 생성

        Args:
            adset_id: 광고 세트 ID
            ad_name: 광고 이름
            video_id: 업로드된 비디오 ID
            message: 광고 메시지
            link: 랜딩 페이지 URL
            page_id: Facebook 페이지 ID
            instagram_actor_id: Instagram 계정 ID (선택사항)
            call_to_action: CTA 버튼 타입
            status: 초기 상태

        Returns:
            생성된 광고 ID
        """
        # 크리에이티브 생성
        video_data = {
            'message': message,
            'video_id': video_id,
            'call_to_action': {
                'type': call_to_action,
                'value': {
                    'link': link
                }
            }
        }

        creative_params = {
            AdCreative.Field.name: f'{ad_name} - Creative',
            AdCreative.Field.object_story_spec: {
                'page_id': page_id,
                'video_data': video_data
            }
        }

        if instagram_actor_id:
            creative_params[AdCreative.Field.object_story_spec]['instagram_actor_id'] = instagram_actor_id

        creative = self.ad_account.create_ad_creative(params=creative_params)

        # 광고 생성
        ad_params = {
            Ad.Field.name: ad_name,
            Ad.Field.adset_id: adset_id,
            Ad.Field.creative: {'creative_id': creative['id']},
            Ad.Field.status: status
        }

        ad = self.ad_account.create_ad(params=ad_params)
        return ad['id']

    def update_ad_status(self, ad_id: str, status: str) -> bool:
        """
        광고 상태 변경

        Args:
            ad_id: 광고 ID
            status: 새로운 상태 (ACTIVE, PAUSED, ARCHIVED)

        Returns:
            성공 여부
        """
        ad = Ad(ad_id)
        ad.update(params={Ad.Field.status: status})
        return True

    @staticmethod
    def create_targeting(
        countries: List[str],
        age_min: int = 18,
        age_max: int = 65,
        genders: Optional[List[int]] = None,
        interests: Optional[List[Dict]] = None,
        locales: Optional[List[int]] = None
    ) -> Dict:
        """
        타겟팅 설정 생성

        Args:
            countries: 국가 코드 리스트 (예: ['KR', 'US'])
            age_min: 최소 연령
            age_max: 최대 연령
            genders: 성별 (1=남성, 2=여성, None=전체)
            interests: 관심사 리스트 (예: [{'id': '6003139266461', 'name': 'Movies'}])
            locales: 언어 코드 리스트 (예: [6] for Korean)

        Returns:
            타겟팅 딕셔너리
        """
        targeting = {
            'geo_locations': {
                'countries': countries
            },
            'age_min': age_min,
            'age_max': age_max
        }

        if genders:
            targeting['genders'] = genders

        if interests:
            targeting['interests'] = interests

        if locales:
            targeting['locales'] = locales

        return targeting


def main():
    """Streamlit 메인 애플리케이션"""

    st.set_page_config(
        page_title="Meta 광고 자동화",
        page_icon="📢",
        layout="wide"
    )

    st.title("📢 Meta 광고 자동화 도구")
    st.markdown("---")

    # 사이드바: API 설정
    with st.sidebar:
        st.header("🔐 API 설정")

        app_id = st.text_input("App ID", type="password")
        app_secret = st.text_input("App Secret", type="password")
        access_token = st.text_input("Access Token", type="password")
        ad_account_id = st.text_input("광고 계정 ID", placeholder="act_xxxxx 또는 숫자만")

        api_configured = all([app_id, app_secret, access_token, ad_account_id])

        if api_configured:
            st.success("✅ API 설정 완료")
        else:
            st.warning("⚠️ API 정보를 입력해주세요")

        st.markdown("---")
        st.markdown("""
        ### 📖 사용 방법
        1. Meta 개발자 센터에서 App 생성
        2. 광고 계정 액세스 권한 부여
        3. 액세스 토큰 생성
        4. 왼쪽에 정보 입력
        """)

    if not api_configured:
        st.info("👈 왼쪽 사이드바에서 API 설정을 완료해주세요")
        return

    # API 초기화
    try:
        automation = MetaAdsAutomation(access_token, ad_account_id, app_id, app_secret)
        st.success("✅ Meta API 연결 성공!")
    except Exception as e:
        st.error(f"❌ API 연결 실패: {str(e)}")
        return

    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 캠페인 조회",
        "🎨 광고 생성",
        "⚙️ 타겟팅 설정",
        "📤 자동 업로드"
    ])

    # 탭 1: 캠페인 조회
    with tab1:
        st.header("📊 기존 캠페인 조회")

        col1, col2 = st.columns([2, 1])
        with col1:
            status_filter = st.multiselect(
                "상태 필터",
                ['ACTIVE', 'PAUSED', 'ARCHIVED', 'DELETED'],
                default=['ACTIVE', 'PAUSED']
            )

        with col2:
            if st.button("🔄 캠페인 새로고침", use_container_width=True):
                st.rerun()

        try:
            campaigns_df = automation.get_campaigns(status_filter)

            if not campaigns_df.empty:
                st.dataframe(campaigns_df, use_container_width=True)

                # 캠페인 선택
                selected_campaign = st.selectbox(
                    "캠페인 선택 (광고 세트 보기)",
                    campaigns_df['ID'].tolist(),
                    format_func=lambda x: campaigns_df[campaigns_df['ID'] == x]['캠페인명'].values[0]
                )

                if selected_campaign:
                    st.subheader(f"📁 광고 세트 목록")
                    adsets_df = automation.get_adsets(selected_campaign)

                    if not adsets_df.empty:
                        st.dataframe(adsets_df, use_container_width=True)
                    else:
                        st.info("이 캠페인에는 광고 세트가 없습니다.")
            else:
                st.info("조회된 캠페인이 없습니다.")

        except Exception as e:
            st.error(f"❌ 오류: {str(e)}")

    # 탭 2: 광고 생성
    with tab2:
        st.header("🎨 새 광고 생성")

        # 캠페인 선택/생성
        st.subheader("1️⃣ 캠페인 선택")

        campaign_option = st.radio(
            "캠페인",
            ["기존 캠페인 사용", "새 캠페인 생성"],
            horizontal=True
        )

        campaign_id = None

        if campaign_option == "기존 캠페인 사용":
            campaigns_df = automation.get_campaigns(['ACTIVE', 'PAUSED'])
            if not campaigns_df.empty:
                campaign_id = st.selectbox(
                    "캠페인 선택",
                    campaigns_df['ID'].tolist(),
                    format_func=lambda x: campaigns_df[campaigns_df['ID'] == x]['캠페인명'].values[0]
                )
            else:
                st.warning("사용 가능한 캠페인이 없습니다. 새 캠페인을 생성하세요.")

        else:  # 새 캠페인 생성
            col1, col2 = st.columns(2)
            with col1:
                new_campaign_name = st.text_input("캠페인명")
            with col2:
                campaign_objective = st.selectbox(
                    "캠페인 목표",
                    ['OUTCOME_TRAFFIC', 'OUTCOME_LEADS', 'OUTCOME_SALES', 'OUTCOME_AWARENESS', 'OUTCOME_ENGAGEMENT']
                )

            if st.button("캠페인 생성"):
                if new_campaign_name:
                    try:
                        campaign_id = automation.create_campaign(
                            new_campaign_name,
                            campaign_objective
                        )
                        st.success(f"✅ 캠페인 생성 완료! ID: {campaign_id}")
                    except Exception as e:
                        st.error(f"❌ 오류: {str(e)}")
                else:
                    st.warning("캠페인명을 입력하세요")

        st.markdown("---")

        # 광고 세트 선택/생성
        if campaign_id:
            st.subheader("2️⃣ 광고 세트 선택")

            adset_option = st.radio(
                "광고 세트",
                ["기존 세트 사용", "새 세트 생성"],
                horizontal=True
            )

            adset_id = None

            if adset_option == "기존 세트 사용":
                adsets_df = automation.get_adsets(campaign_id)
                if not adsets_df.empty:
                    adset_id = st.selectbox(
                        "광고 세트 선택",
                        adsets_df['ID'].tolist(),
                        format_func=lambda x: adsets_df[adsets_df['ID'] == x]['광고세트명'].values[0]
                    )
                else:
                    st.warning("이 캠페인에는 광고 세트가 없습니다. 새 세트를 생성하세요.")

            else:  # 새 광고 세트 생성
                with st.form("adset_form"):
                    adset_name = st.text_input("광고 세트명")

                    col1, col2 = st.columns(2)
                    with col1:
                        daily_budget = st.number_input("일일 예산 (USD)", min_value=1.0, value=10.0, step=1.0)
                    with col2:
                        optimization_goal = st.selectbox(
                            "최적화 목표",
                            ['REACH', 'IMPRESSIONS', 'LINK_CLICKS', 'CONVERSIONS']
                        )

                    # 간단한 타겟팅
                    st.write("**타겟팅 설정**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        countries = st.multiselect("국가", ['KR', 'US', 'JP', 'CN'], default=['KR'])
                    with col2:
                        age_min = st.number_input("최소 연령", 18, 65, 18)
                    with col3:
                        age_max = st.number_input("최대 연령", 18, 65, 65)

                    submit_adset = st.form_submit_button("광고 세트 생성")

                    if submit_adset and adset_name:
                        try:
                            targeting = MetaAdsAutomation.create_targeting(
                                countries=countries,
                                age_min=age_min,
                                age_max=age_max
                            )

                            adset_id = automation.create_adset(
                                campaign_id=campaign_id,
                                adset_name=adset_name,
                                daily_budget=int(daily_budget * 100),  # USD to cents
                                targeting=targeting,
                                optimization_goal=optimization_goal
                            )
                            st.success(f"✅ 광고 세트 생성 완료! ID: {adset_id}")
                        except Exception as e:
                            st.error(f"❌ 오류: {str(e)}")

            st.markdown("---")

            # 광고 생성
            if adset_id:
                st.subheader("3️⃣ 광고 크리에이티브")

                with st.form("ad_form"):
                    ad_name = st.text_input("광고명")
                    message = st.text_area("광고 메시지")
                    link = st.text_input("랜딩 페이지 URL")
                    page_id = st.text_input("Facebook 페이지 ID")

                    col1, col2 = st.columns(2)
                    with col1:
                        creative_type = st.radio("크리에이티브 타입", ["이미지", "비디오"])
                    with col2:
                        cta_type = st.selectbox(
                            "CTA 버튼",
                            ['LEARN_MORE', 'SHOP_NOW', 'SIGN_UP', 'DOWNLOAD', 'CONTACT_US']
                        )

                    uploaded_file = st.file_uploader(
                        f"{creative_type} 업로드",
                        type=['jpg', 'jpeg', 'png'] if creative_type == "이미지" else ['mp4', 'mov']
                    )

                    submit_ad = st.form_submit_button("광고 생성 (PAUSED 상태)")

                    if submit_ad:
                        if not all([ad_name, message, link, page_id, uploaded_file]):
                            st.warning("모든 필드를 입력해주세요")
                        else:
                            try:
                                # 파일 저장
                                file_path = f"/tmp/{uploaded_file.name}"
                                with open(file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())

                                # 업로드 및 광고 생성
                                if creative_type == "이미지":
                                    with st.spinner("이미지 업로드 중..."):
                                        image_hash = automation.upload_image(file_path)

                                    with st.spinner("광고 생성 중..."):
                                        ad_id = automation.create_image_ad(
                                            adset_id=adset_id,
                                            ad_name=ad_name,
                                            image_hash=image_hash,
                                            message=message,
                                            link=link,
                                            page_id=page_id,
                                            call_to_action=cta_type
                                        )
                                else:  # 비디오
                                    with st.spinner("비디오 업로드 중... (시간이 걸릴 수 있습니다)"):
                                        video_id = automation.upload_video(file_path)

                                    with st.spinner("광고 생성 중..."):
                                        ad_id = automation.create_video_ad(
                                            adset_id=adset_id,
                                            ad_name=ad_name,
                                            video_id=video_id,
                                            message=message,
                                            link=link,
                                            page_id=page_id,
                                            call_to_action=cta_type
                                        )

                                st.success(f"✅ 광고 생성 완료! ID: {ad_id}")
                                st.info("광고가 PAUSED 상태로 생성되었습니다. 검토 후 활성화하세요.")

                                # 파일 삭제
                                os.remove(file_path)

                            except Exception as e:
                                st.error(f"❌ 오류: {str(e)}")

    # 탭 3: 타겟팅 설정
    with tab3:
        st.header("⚙️ 타겟팅 템플릿")

        st.markdown("""
        타겟팅 설정을 미리 구성하고 저장할 수 있습니다.
        """)

        with st.form("targeting_template"):
            template_name = st.text_input("템플릿명")

            col1, col2 = st.columns(2)
            with col1:
                countries = st.multiselect(
                    "국가",
                    ['KR', 'US', 'JP', 'CN', 'TW', 'HK', 'SG'],
                    default=['KR']
                )
                age_min = st.slider("최소 연령", 18, 65, 18)
                age_max = st.slider("최대 연령", 18, 65, 65)

            with col2:
                genders = st.multiselect("성별", [1, 2], format_func=lambda x: "남성" if x == 1 else "여성")
                locales = st.multiselect("언어", [6, 24], format_func=lambda x: "한국어" if x == 6 else "영어")

            st.write("**관심사 (Interest ID 입력)**")
            st.info("Meta Ads Manager에서 관심사 ID를 확인할 수 있습니다.")
            interest_ids = st.text_area("관심사 ID (줄바꿈으로 구분)", placeholder="6003139266461\n6003397425735")

            save_template = st.form_submit_button("템플릿 저장")

            if save_template and template_name:
                # 타겟팅 구성
                interests = []
                if interest_ids:
                    for interest_id in interest_ids.strip().split('\n'):
                        if interest_id.strip():
                            interests.append({'id': interest_id.strip()})

                targeting = MetaAdsAutomation.create_targeting(
                    countries=countries,
                    age_min=age_min,
                    age_max=age_max,
                    genders=genders if genders else None,
                    interests=interests if interests else None,
                    locales=locales if locales else None
                )

                # 세션 상태에 저장
                if 'targeting_templates' not in st.session_state:
                    st.session_state.targeting_templates = {}

                st.session_state.targeting_templates[template_name] = targeting
                st.success(f"✅ 템플릿 '{template_name}' 저장 완료!")
                st.json(targeting)

        # 저장된 템플릿 목록
        if 'targeting_templates' in st.session_state and st.session_state.targeting_templates:
            st.subheader("📋 저장된 템플릿")
            for name, targeting in st.session_state.targeting_templates.items():
                with st.expander(name):
                    st.json(targeting)

    # 탭 4: 자동 업로드
    with tab4:
        st.header("📤 크리에이티브 일괄 업로드")

        st.markdown("""
        여러 개의 이미지/비디오를 한 번에 업로드하고 광고를 자동 생성합니다.
        """)

        # 기본 설정
        campaigns_df = automation.get_campaigns(['ACTIVE', 'PAUSED'])
        if campaigns_df.empty:
            st.warning("먼저 캠페인을 생성하세요.")
        else:
            selected_campaign = st.selectbox(
                "대상 캠페인",
                campaigns_df['ID'].tolist(),
                format_func=lambda x: campaigns_df[campaigns_df['ID'] == x]['캠페인명'].values[0],
                key="batch_campaign"
            )

            if selected_campaign:
                adsets_df = automation.get_adsets(selected_campaign)

                if not adsets_df.empty:
                    selected_adset = st.selectbox(
                        "대상 광고 세트",
                        adsets_df['ID'].tolist(),
                        format_func=lambda x: adsets_df[adsets_df['ID'] == x]['광고세트명'].values[0]
                    )

                    # 공통 설정
                    col1, col2 = st.columns(2)
                    with col1:
                        message_template = st.text_area("광고 메시지 템플릿")
                        link_url = st.text_input("랜딩 페이지 URL")
                    with col2:
                        page_id = st.text_input("Facebook 페이지 ID", key="batch_page_id")
                        cta = st.selectbox(
                            "CTA 버튼",
                            ['LEARN_MORE', 'SHOP_NOW', 'SIGN_UP', 'DOWNLOAD', 'CONTACT_US'],
                            key="batch_cta"
                        )

                    # 파일 업로드
                    uploaded_files = st.file_uploader(
                        "크리에이티브 파일 (여러 개 선택 가능)",
                        type=['jpg', 'jpeg', 'png', 'mp4', 'mov'],
                        accept_multiple_files=True
                    )

                    if uploaded_files and st.button("🚀 일괄 광고 생성", type="primary"):
                        if not all([message_template, link_url, page_id]):
                            st.warning("모든 공통 설정을 입력하세요")
                        else:
                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            success_count = 0
                            error_count = 0

                            for i, uploaded_file in enumerate(uploaded_files):
                                try:
                                    status_text.text(f"처리 중: {uploaded_file.name} ({i+1}/{len(uploaded_files)})")

                                    # 파일 저장
                                    file_path = f"/tmp/{uploaded_file.name}"
                                    with open(file_path, "wb") as f:
                                        f.write(uploaded_file.getbuffer())

                                    # 파일 타입 확인
                                    is_video = uploaded_file.name.lower().endswith(('.mp4', '.mov'))

                                    ad_name = f"Auto - {os.path.splitext(uploaded_file.name)[0]}"

                                    if is_video:
                                        video_id = automation.upload_video(file_path)
                                        ad_id = automation.create_video_ad(
                                            adset_id=selected_adset,
                                            ad_name=ad_name,
                                            video_id=video_id,
                                            message=message_template,
                                            link=link_url,
                                            page_id=page_id,
                                            call_to_action=cta
                                        )
                                    else:
                                        image_hash = automation.upload_image(file_path)
                                        ad_id = automation.create_image_ad(
                                            adset_id=selected_adset,
                                            ad_name=ad_name,
                                            image_hash=image_hash,
                                            message=message_template,
                                            link=link_url,
                                            page_id=page_id,
                                            call_to_action=cta
                                        )

                                    success_count += 1
                                    os.remove(file_path)

                                except Exception as e:
                                    error_count += 1
                                    st.error(f"❌ {uploaded_file.name}: {str(e)}")

                                progress_bar.progress((i + 1) / len(uploaded_files))

                            status_text.text("완료!")
                            st.success(f"✅ 성공: {success_count}개 | ❌ 실패: {error_count}개")

                else:
                    st.warning("이 캠페인에는 광고 세트가 없습니다. 먼저 광고 세트를 생성하세요.")


if __name__ == "__main__":
    main()
