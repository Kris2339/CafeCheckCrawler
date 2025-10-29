import requests
from bs4 import BeautifulSoup
import os
import time
import random
import pandas as pd
from datetime import datetime
from urllib.parse import quote
import html as html_module
import re

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
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
    }
    if headers:
        h.update(headers)
    return requests.get(url, headers=h, timeout=timeout)

def search_naver(keyword):
    url = f"{BASE_SEARCH}{quote(keyword)}"
    r = req_get(url)
    if r.status_code != 200:
        return None, url
    return r.text, url

def find_popular_posts_section(html, search_url):
    """
    '인기글' 더보기 URL을 최대한 견고하게 찾는다.
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
    for el in soup.find_all(text=lambda t: t and "인기글" in t):
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

def extract_cafe_name_from_url(url):
    """URL에서 카페 ID 추출"""
    try:
        part = url.split("cafe.naver.com/")[1]
        cafe_id = part.split("/")[0].split("?")[0]
        return cafe_id
    except Exception:
        return "알 수 없음"

def extract_cafe_name_from_text(text):
    """텍스트에서 카페명 추출 (매핑 사용)"""
    if not text:
        return None
    for keyword, simple_name in CAFE_NAME_MAPPING.items():
        if keyword in text:
            return simple_name
    return None

def find_cafe_posts_in_top20(html):
    """
    개선된 카페 글 추출 로직
    - 더 넓은 범위에서 카페명 검색
    - 다양한 HTML 구조 지원
    - URL에서 카페 ID 추출 기능 강화
    """
    soup = BeautifulSoup(html, "html.parser")

    # 모든 cafe.naver.com 링크 찾기
    all_cafe_links = soup.select('a[href*="cafe.naver.com"]')

    candidates = []
    seen_urls = set()

    for a in all_cafe_links:
        href = a.get("href", "")
        if not href or href in seen_urls:
            continue
        seen_urls.add(href)

        # 제목 추출: 링크 텍스트를 우선 사용
        title = a.get_text(strip=True)

        # 부모 요소들을 순회하며 더 큰 컨텍스트 찾기
        card = None
        for parent in [a.parent, a.parent.parent if a.parent else None,
                      a.parent.parent.parent if a.parent and a.parent.parent else None]:
            if parent and hasattr(parent, 'name'):
                # 일반적인 카드 컨테이너 찾기
                if parent.name in ['li', 'div', 'article'] and parent.get('class'):
                    card = parent
                    break

        # 카드를 못 찾으면 상위 10개 부모 중에서 찾기
        if not card:
            current = a
            for _ in range(10):
                current = current.parent if current and hasattr(current, 'parent') else None
                if not current:
                    break
                if current.name in ['li', 'div', 'article']:
                    card = current
                    break

        # 제목이 없거나 너무 짧으면 카드에서 찾기
        if (not title or len(title) < 5) and card:
            # 제목을 찾는 다양한 시도
            title_candidates = []

            # 1. strong, h3, .title 등의 태그에서 찾기
            for selector in ['strong', 'h3', 'h4', '.title', '[class*="title"]',
                           '[class*="Title"]', 'span[class*="text"]']:
                title_elem = card.select_one(selector)
                if title_elem:
                    t = title_elem.get_text(strip=True)
                    if t and len(t) > 5:
                        title_candidates.append(t)

            # 2. 링크 근처의 텍스트 노드에서 찾기
            next_elem = a.find_next_sibling()
            if next_elem:
                t = next_elem.get_text(strip=True)
                if t and len(t) > 5:
                    title_candidates.append(t)

            # 가장 긴 것을 제목으로 선택
            if title_candidates:
                title = max(title_candidates, key=len)

        # 여전히 제목이 없으면 "제목 없음"
        if not title or len(title) < 3:
            title = "제목 없음"

        # 카페명 추출: 여러 방법 시도
        cafe_name = None

        if card:
            # 카드 전체 텍스트에서 매핑 검색
            card_text = card.get_text(" ", strip=True)
            cafe_name = extract_cafe_name_from_text(card_text)

            # 특정 선택자에서도 시도
            if not cafe_name:
                for selector in ['.source', '.source_box', '[class*="source"]',
                               '[class*="profile"]', '.info', '[class*="info"]',
                               '.sub_txt', '[class*="sub"]', '[class*="name"]']:
                    elem = card.select_one(selector)
                    if elem:
                        text = elem.get_text(" ", strip=True)
                        cafe_name = extract_cafe_name_from_text(text)
                        if cafe_name:
                            break

        # 카페명을 못 찾으면 URL에서 카페 ID 사용
        if not cafe_name:
            cafe_name = extract_cafe_name_from_url(href)

        candidates.append({
            "title": title[:100],  # 제목 길이 제한
            "cafe_name": cafe_name,
            "cafe_id": extract_cafe_name_from_url(href),
            "url": href
        })

        # 20개면 충분
        if len(candidates) >= 20:
            break

    # 순위 부여
    for i, item in enumerate(candidates[:20], 1):
        item["rank"] = i

    return candidates[:20]

def read_keyword_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return []

def process_keyword(keyword):
    result = {
        "keyword": keyword,
        "has_popular_section": False,
        "has_more_button": False,
        "cafe_count": 0,
        "cafe_names": "",
        "error": ""
    }
    try:
        html, search_url = search_naver(keyword)
        if not html:
            result["error"] = "검색 실패"
            return result

        time.sleep(random.uniform(1, 2))

        section = find_popular_posts_section(html, search_url)
        if not section.get("found"):
            result["error"] = "인기글 섹션 없음"
            return result
        result["has_popular_section"] = True

        if not section.get("more_url"):
            result["error"] = "더보기 버튼 없음"
            return result
        result["has_more_button"] = True

        time.sleep(random.uniform(1, 2))

        more_html = fetch_more_page(section["more_url"], referer=section.get("referer"))
        if not more_html:
            result["error"] = "더보기 페이지 실패"
            return result

        time.sleep(random.uniform(1, 2))

        cafe_posts = find_cafe_posts_in_top20(more_html)
        if cafe_posts:
            result["cafe_count"] = len(cafe_posts)
            result["cafe_names"] = ", ".join([p["cafe_name"] for p in cafe_posts])
        else:
            result["error"] = "카페 글 없음"

        return result
    except Exception as e:
        result["error"] = f"오류: {e}"
        return result

def save_to_excel(results, output_path):
    df = pd.DataFrame(results)
    df.to_excel(output_path, index=False, engine="openpyxl")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    keyword_file = os.path.join(current_dir, "키워드 리스트.txt")
    keywords = read_keyword_file(keyword_file)

    if not keywords:
        keyword = input("키워드 입력: ").strip()
        keywords = [keyword] if keyword else []

    all_results = []
    n = len(keywords)

    for i, kw in enumerate(keywords, 1):
        res = process_keyword(kw)
        all_results.append(res)

        # 간결 출력
        status = []
        status.append(f"인기글:{'O' if res['has_popular_section'] else 'X'}")
        status.append(f"더보기:{'O' if res['has_more_button'] else 'X'}")
        status.append(f"카페:{res['cafe_count']}개")
        err = res['error'] if res['error'] else "-"
        print(f"[{i}/{n}] {kw} | " + " | ".join(status) + f" | 오류:{err}")

        if i < n:
            time.sleep(random.uniform(3, 5))

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(current_dir, f"크롤링_결과_{ts}.xlsx")
    save_to_excel(all_results, out)

    # 최종 요약
    has_pop = sum(1 for r in all_results if r["has_popular_section"])
    has_more = sum(1 for r in all_results if r["has_more_button"])
    has_cafe = sum(1 for r in all_results if r["cafe_count"] > 0)
    print(f"\n총:{len(all_results)} | 인기글:{has_pop} | 더보기:{has_more} | 카페≥1:{has_cafe}")
    print(f"파일:{out}")

if __name__ == "__main__":
    main()
