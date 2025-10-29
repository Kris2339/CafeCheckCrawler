import requests
from bs4 import BeautifulSoup
import os
import time
import random
import pandas as pd
from datetime import datetime
from urllib.parse import quote
import html as html_module
import urllib3

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========================================
# 카페명 매핑 규칙
# ========================================
CAFE_NAME_MAPPING = {
    "척추질환": "척추질환",
    "헤이든": "헤이든",
    "여우야": "여우야",
    "줌마렐라": "줌마렐라",
    "씨씨앙": "씨씨앙",
    "재잘재잘": "재잘재잘",
    "쇼핑매니아": "쇼핑매니아",
    "세종맘놀이터": "세종맘놀이터",
    "경기광주맘카페": "광주맘",
    "천아맘": "천아맘",
    "예카": "예카",
    "불면증": "불면증",
    "고고당": "고고당",
    "키작은 아이": "키작은",
    "라준사": "라준사",
    "대구맘": "대구맘",
    "맘피스": "맘피스",
    "웨딩킹": "웨딩킹",
    "갑상선포럼": "갑상선포럼",
    "느린걸음": "느린걸음",
    "방판매니아": "방판매니아",
    "해피돌싱": "해피돌싱",
    "강남엄마": "강남엄마",
    "내집갖기": "내집갖기",
    "키크는방법": "키크는방법",
    "유방암": "유방암",
    "미사맘": "미사맘",
    "이명극복": "이명극복",
    "은퇴 후 50년": "은퇴 50",
    "아띠아모": "아띠아모",
    "당뇨와건강": "당뇨와건강",
    "비그룸": "비그룸",
    "루이클럽": "루이클럽",
    "코사모": "코사모",
    "함께해요건강생활": "함께해요건강생활",
    "신장병": "신장병 환우"
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
BASE_SEARCH = "https://search.naver.com/search.naver?query="

def simplify_cafe_name(cafe_name: str) -> str:
    for keyword, simple_name in CAFE_NAME_MAPPING.items():
        if keyword in cafe_name:
            return simple_name
    return cafe_name

def req_get(url, headers=None, timeout=10):
    h = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }
    if headers:
        h.update(headers)
    return requests.get(url, headers=h, timeout=timeout, verify=False)

def search_naver(keyword):
    url = f"{BASE_SEARCH}{quote(keyword)}"
    try:
        r = req_get(url)
        print(f"  요청 URL: {url}")
        print(f"  응답 상태: {r.status_code}")
        if r.status_code != 200:
            print(f"  응답 내용 (처음 200자): {r.text[:200]}")
            return None, url
        return r.text, url
    except Exception as e:
        print(f"  예외 발생: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None, url

import re
from bs4 import BeautifulSoup

def find_popular_posts_section(html, search_url):
    """
    '인기글' 더보기 URL을 최대한 견고하게 찾는다.
    1) a[data-lb-trigger^="/p/ugc"] (최우선)
    2) a[href^="/p/ugc"]
    3) '인기글' 텍스트 주변에서 a[data-lb-trigger] 또는 '더보기' 포함 앵커
    4) 정규식으로 /p/ugc 경로 추출
    """
    soup = BeautifulSoup(html, "html.parser")

    # 1) data-lb-trigger가 /p/ugc로 시작하는 앵커
    a = soup.select_one('a[data-lb-trigger^="/p/ugc"]')
    if a:
        return {
            "found": True,
            "title": "인기글",
            "more_url": a.get("data-lb-trigger"),
            "referer": search_url
        }

    # 2) href가 /p/ugc로 시작
    a = soup.select_one('a[href^="/p/ugc"]')
    if a:
        return {
            "found": True,
            "title": "인기글",
            "more_url": a.get("href"),
            "referer": search_url
        }

    # 3) '인기글' 텍스트 기준으로 범위 좁혀 탐색
    hit = None
    for el in soup.find_all(text=lambda t: t and "인기글" in t):
        # 근처 부모 블록
        blk = None
        for parent in (el.parent, el.parent and el.parent.parent):
            if getattr(parent, "name", None):
                blk = parent
                break
        ctx = blk or soup
        # 더보기 텍스트가 있는 앵커
        for s in ctx.find_all("span"):
            if s.string and "더보기" in s.string:
                a = s.find_parent("a")
                if a and (a.get("data-lb-trigger") or a.get("href")):
                    more = a.get("data-lb-trigger") or a.get("href")
                    if more and more != "#":
                        return {
                            "found": True,
                            "title": "인기글",
                            "more_url": more,
                            "referer": search_url
                        }
        # data-lb-trigger가 있는 임의 앵커
        a = ctx.find("a", attrs={"data-lb-trigger": True})
        if a:
            return {
                "found": True,
                "title": "인기글",
                "more_url": a.get("data-lb-trigger"),
                "referer": search_url
            }

    # 4) HTML 원문에서 정규식으로 /p/ugc 경로 추출
    m = re.search(r'["\'](/p/ugc[^"\']+)["\']', html)
    if m:
        return {
            "found": True,
            "title": "인기글",
            "more_url": m.group(1),
            "referer": search_url
        }

    return {"found": False, "more_url": None, "referer": search_url}


def fetch_more_page(url, referer=None):
    if not url:
        return None
    if url.startswith("http"):
        full = url
    else:
        if url.startswith("/p/ugc") or url.startswith("/ugc"):
            full = "https://s.search.naver.com" + url
        else:
            full = "https://search.naver.com" + url

    r = req_get(full, headers={"Referer": referer or "https://search.naver.com/"})
    if r.status_code != 200:
        return None

    # JSON 응답 처리
    try:
        j = r.json()
        html_content = ""
        if "dom" in j and "collection" in j["dom"]:
            for item in j["dom"]["collection"]:
                if "html" in item:
                    html_content += html_module.unescape(item["html"])
        if html_content:
            return html_content
    except Exception:
        pass
    return r.text

def find_cafe_posts_in_top20(html):
    """디버깅 정보를 추가한 버전"""
    soup = BeautifulSoup(html, "html.parser")

    print("\n=== 디버깅: HTML 분석 시작 ===")

    # 모든 cafe.naver.com 링크 찾기
    all_cafe_links = soup.select('a[href*="cafe.naver.com"]')
    print(f"총 {len(all_cafe_links)}개의 카페 링크 발견")

    if len(all_cafe_links) == 0:
        print("경고: cafe.naver.com 링크를 찾을 수 없습니다!")
        # HTML 일부 출력
        print("HTML 샘플 (처음 500자):")
        print(html[:500])

    candidates = []
    for idx, a in enumerate(all_cafe_links[:30], 1):  # 처음 30개만 디버깅
        print(f"\n--- 링크 {idx} ---")
        print(f"href: {a.get('href', '')}")

        card = a.find_parent(["div", "li", "article"])
        if not card:
            print("부모 카드를 찾을 수 없음")
            continue

        title = (a.get_text() or "").strip()
        if not title:
            t = card.find(["strong", "span"], attrs={"class": lambda c: c and "title" in c})
            title = t.get_text(strip=True) if t else "제목 없음"
        print(f"제목: {title}")

        cafe_name = "알 수 없음"
        source = None
        for sel in [".sds-comps-profile", ".source_box", ".info_group", ".sub_txt", ".detail_area"]:
            source = card.select_one(sel)
            if source:
                print(f"소스 발견: {sel}")
                break

        if source:
            txt = source.get_text(" ", strip=True)
            print(f"소스 텍스트: {txt}")
            for kw, nm in CAFE_NAME_MAPPING.items():
                if kw in txt:
                    cafe_name = nm
                    print(f"매핑된 카페명: {cafe_name}")
                    break
        else:
            print("소스 정보를 찾을 수 없음")

        href = a.get("href", "")
        cafe_id = "알 수 없음"
        try:
            part = href.split("cafe.naver.com/")[1]
            cafe_id = part.split("/")[0].split("?")[0]
            print(f"카페 ID: {cafe_id}")
        except Exception:
            print("카페 ID 추출 실패")

        candidates.append({
            "title": title or "제목 없음",
            "cafe_name": cafe_name,
            "cafe_id": cafe_id,
            "url": href
        })

    # 중복 제거 및 상위 20개
    cafe_posts, seen = [], set()
    for item in candidates:
        key = (item["url"], item["title"])
        if key in seen:
            continue
        seen.add(key)
        cafe_posts.append(item)
        if len(cafe_posts) >= 20:
            break

    for i, it in enumerate(cafe_posts, 1):
        it["rank"] = i

    print(f"\n=== 최종 결과: {len(cafe_posts)}개의 카페 글 ===")
    return cafe_posts

# 간단한 테스트 함수
def test_keyword(keyword):
    print(f"\n{'='*50}")
    print(f"키워드 테스트: {keyword}")
    print(f"{'='*50}\n")

    # 1단계: 검색
    print("1단계: 네이버 검색...")
    html, search_url = search_naver(keyword)
    if not html:
        print("❌ 검색 실패")
        return
    print(f"✓ 검색 성공 (HTML 길이: {len(html)})")

    # 2단계: 인기글 섹션 찾기
    print("\n2단계: 인기글 섹션 찾기...")
    section = find_popular_posts_section(html, search_url)
    if not section.get("found"):
        print("❌ 인기글 섹션 없음")
        return
    print(f"✓ 인기글 섹션 발견")
    print(f"  더보기 URL: {section.get('more_url')}")

    if not section.get("more_url"):
        print("❌ 더보기 버튼 없음")
        return

    # 3단계: 더보기 페이지 가져오기
    print("\n3단계: 더보기 페이지 가져오기...")
    time.sleep(1)
    more_html = fetch_more_page(section["more_url"], referer=section.get("referer"))
    if not more_html:
        print("❌ 더보기 페이지 가져오기 실패")
        return
    print(f"✓ 더보기 페이지 가져오기 성공 (HTML 길이: {len(more_html)})")

    # HTML 저장 (디버깅용)
    debug_file = f"/tmp/debug_{keyword}.html"
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(more_html)
    print(f"  디버깅용 HTML 저장: {debug_file}")

    # 4단계: 카페 글 추출
    print("\n4단계: 카페 글 추출...")
    cafe_posts = find_cafe_posts_in_top20(more_html)

    if cafe_posts:
        print(f"\n✓ {len(cafe_posts)}개의 카페 글 추출 성공:")
        for post in cafe_posts[:5]:  # 처음 5개만 출력
            print(f"  {post['rank']}. [{post['cafe_name']}] {post['title'][:50]}")
    else:
        print("❌ 카페 글 추출 실패")

if __name__ == "__main__":
    test_keyword("당뇨에좋은음식")
