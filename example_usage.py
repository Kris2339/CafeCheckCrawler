"""
Meta Ads Automation - Example Usage
====================================
프로그래밍 방식으로 Meta 광고를 생성하는 예제 코드

이 파일은 Streamlit UI 없이 순수 Python 코드로 광고를 생성하는 방법을 보여줍니다.
"""

from meta_ads_automation import MetaAdsAutomation
import os
from datetime import datetime, timedelta

# 환경 변수에서 인증 정보 로드 (또는 직접 입력)
APP_ID = os.getenv('META_APP_ID', 'your_app_id')
APP_SECRET = os.getenv('META_APP_SECRET', 'your_app_secret')
ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN', 'your_access_token')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID', 'act_123456789')
PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', 'your_page_id')


def example_1_list_campaigns():
    """예제 1: 기존 캠페인 목록 조회"""
    print("=" * 60)
    print("예제 1: 캠페인 목록 조회")
    print("=" * 60)

    automation = MetaAdsAutomation(ACCESS_TOKEN, AD_ACCOUNT_ID, APP_ID, APP_SECRET)

    # 활성 및 일시정지된 캠페인 조회
    campaigns = automation.get_campaigns(['ACTIVE', 'PAUSED'])

    print(f"\n총 {len(campaigns)}개의 캠페인을 찾았습니다:\n")
    print(campaigns.to_string())


def example_2_create_complete_campaign():
    """예제 2: 캠페인-광고세트-광고를 한 번에 생성"""
    print("\n" + "=" * 60)
    print("예제 2: 완전한 광고 캠페인 생성")
    print("=" * 60)

    automation = MetaAdsAutomation(ACCESS_TOKEN, AD_ACCOUNT_ID, APP_ID, APP_SECRET)

    # 1. 캠페인 생성
    print("\n1️⃣ 캠페인 생성 중...")
    campaign_name = f"자동화 테스트 캠페인 - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    campaign_id = automation.create_campaign(
        campaign_name=campaign_name,
        objective='OUTCOME_TRAFFIC',  # 트래픽 목표
        status='PAUSED'  # 일시정지 상태로 생성
    )
    print(f"✅ 캠페인 생성 완료: {campaign_id}")

    # 2. 타겟팅 설정
    print("\n2️⃣ 타겟팅 설정 중...")
    targeting = MetaAdsAutomation.create_targeting(
        countries=['KR'],  # 한국
        age_min=25,
        age_max=45,
        genders=[1, 2],  # 모든 성별
        locales=[6]  # 한국어
    )
    print("✅ 타겟팅 설정 완료")

    # 3. 광고 세트 생성
    print("\n3️⃣ 광고 세트 생성 중...")
    adset_name = f"자동화 광고 세트 - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    adset_id = automation.create_adset(
        campaign_id=campaign_id,
        adset_name=adset_name,
        daily_budget=1000,  # $10/일 (센트 단위)
        targeting=targeting,
        billing_event='IMPRESSIONS',
        optimization_goal='REACH'
    )
    print(f"✅ 광고 세트 생성 완료: {adset_id}")

    # 4. 이미지 업로드 및 광고 생성
    print("\n4️⃣ 광고 생성 중...")
    print("   (이미지 파일 경로를 지정해야 합니다)")

    # 주의: 실제 이미지 파일 경로를 지정해야 합니다
    # image_hash = automation.upload_image('/path/to/your/image.jpg')
    #
    # ad_id = automation.create_image_ad(
    #     adset_id=adset_id,
    #     ad_name="자동화 이미지 광고",
    #     image_hash=image_hash,
    #     message="이것은 자동으로 생성된 테스트 광고입니다!",
    #     link="https://example.com",
    #     page_id=PAGE_ID,
    #     call_to_action='LEARN_MORE'
    # )
    # print(f"✅ 광고 생성 완료: {ad_id}")

    print("\n" + "=" * 60)
    print(f"✅ 전체 프로세스 완료!")
    print(f"   캠페인 ID: {campaign_id}")
    print(f"   광고 세트 ID: {adset_id}")
    print("=" * 60)


def example_3_batch_upload_images():
    """예제 3: 여러 이미지를 한 번에 업로드하고 광고 생성"""
    print("\n" + "=" * 60)
    print("예제 3: 일괄 이미지 광고 생성")
    print("=" * 60)

    automation = MetaAdsAutomation(ACCESS_TOKEN, AD_ACCOUNT_ID, APP_ID, APP_SECRET)

    # 기존 캠페인과 광고 세트 사용
    # 주의: 실제 ID로 변경 필요
    campaign_id = "YOUR_CAMPAIGN_ID"
    adset_id = "YOUR_ADSET_ID"

    # 업로드할 이미지 목록
    images = [
        "/path/to/image1.jpg",
        "/path/to/image2.jpg",
        "/path/to/image3.jpg",
    ]

    print(f"\n{len(images)}개의 이미지 광고를 생성합니다...\n")

    for i, image_path in enumerate(images, 1):
        try:
            print(f"[{i}/{len(images)}] {image_path} 처리 중...")

            # 이미지 업로드
            image_hash = automation.upload_image(image_path)

            # 광고 생성
            ad_name = f"자동화 광고 #{i} - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ad_id = automation.create_image_ad(
                adset_id=adset_id,
                ad_name=ad_name,
                image_hash=image_hash,
                message=f"자동으로 생성된 광고 #{i}",
                link="https://example.com",
                page_id=PAGE_ID,
                call_to_action='LEARN_MORE'
            )

            print(f"   ✅ 광고 생성 완료: {ad_id}\n")

        except Exception as e:
            print(f"   ❌ 오류 발생: {str(e)}\n")

    print("=" * 60)
    print("✅ 일괄 업로드 완료!")
    print("=" * 60)


def example_4_create_video_ad():
    """예제 4: 비디오 광고 생성"""
    print("\n" + "=" * 60)
    print("예제 4: 비디오 광고 생성")
    print("=" * 60)

    automation = MetaAdsAutomation(ACCESS_TOKEN, AD_ACCOUNT_ID, APP_ID, APP_SECRET)

    # 기존 광고 세트 사용
    adset_id = "YOUR_ADSET_ID"

    print("\n비디오 업로드 중... (시간이 걸릴 수 있습니다)")

    # 비디오 업로드
    # video_id = automation.upload_video('/path/to/video.mp4')
    # print(f"✅ 비디오 업로드 완료: {video_id}")

    # 비디오 광고 생성
    # ad_id = automation.create_video_ad(
    #     adset_id=adset_id,
    #     ad_name="자동화 비디오 광고",
    #     video_id=video_id,
    #     message="흥미로운 비디오 광고입니다!",
    #     link="https://example.com",
    #     page_id=PAGE_ID,
    #     call_to_action='WATCH_MORE'
    # )
    # print(f"✅ 광고 생성 완료: {ad_id}")


def example_5_advanced_targeting():
    """예제 5: 고급 타겟팅 옵션"""
    print("\n" + "=" * 60)
    print("예제 5: 고급 타겟팅 설정")
    print("=" * 60)

    # 예시: 다양한 타겟팅 조합
    targeting_examples = {
        "한국 20-30대 남성": MetaAdsAutomation.create_targeting(
            countries=['KR'],
            age_min=20,
            age_max=30,
            genders=[1],  # 남성만
            locales=[6]  # 한국어
        ),

        "미국 전연령 영어 사용자": MetaAdsAutomation.create_targeting(
            countries=['US'],
            age_min=18,
            age_max=65,
            locales=[24]  # 영어
        ),

        "아시아 여러 국가": MetaAdsAutomation.create_targeting(
            countries=['KR', 'JP', 'CN', 'TW', 'HK'],
            age_min=25,
            age_max=45
        ),
    }

    for name, targeting in targeting_examples.items():
        print(f"\n타겟팅 예시: {name}")
        print("-" * 40)
        import json
        print(json.dumps(targeting, indent=2, ensure_ascii=False))


def example_6_manage_ad_status():
    """예제 6: 광고 상태 관리"""
    print("\n" + "=" * 60)
    print("예제 6: 광고 상태 변경")
    print("=" * 60)

    automation = MetaAdsAutomation(ACCESS_TOKEN, AD_ACCOUNT_ID, APP_ID, APP_SECRET)

    # 광고 ID (실제 ID로 변경 필요)
    ad_id = "YOUR_AD_ID"

    print("\n광고 상태를 변경할 수 있습니다:")
    print("- ACTIVE: 광고 활성화")
    print("- PAUSED: 광고 일시정지")
    print("- ARCHIVED: 광고 보관 (재활성화 불가)")

    # 예시: 광고 활성화
    # automation.update_ad_status(ad_id, 'ACTIVE')
    # print(f"✅ 광고 {ad_id}가 활성화되었습니다")

    # 예시: 광고 일시정지
    # automation.update_ad_status(ad_id, 'PAUSED')
    # print(f"✅ 광고 {ad_id}가 일시정지되었습니다")


def main():
    """메인 함수: 모든 예제 실행"""
    print("\n")
    print("=" * 60)
    print("Meta 광고 자동화 - 사용 예제")
    print("=" * 60)
    print("\n⚠️  주의: 이 스크립트를 실행하기 전에:")
    print("1. 환경 변수를 설정하거나 코드에서 직접 인증 정보 입력")
    print("2. 실제 이미지/비디오 파일 경로 지정")
    print("3. 캠페인/광고세트 ID를 실제 ID로 변경")
    print("\n각 예제 함수의 주석을 해제하고 실행하세요.\n")

    # 예제 실행 (원하는 예제만 주석 해제)
    try:
        # example_1_list_campaigns()
        # example_2_create_complete_campaign()
        # example_3_batch_upload_images()
        # example_4_create_video_ad()
        example_5_advanced_targeting()
        # example_6_manage_ad_status()

        print("\n✅ 스크립트 실행 완료!")

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
