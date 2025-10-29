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

# 디버그 모드 설정
DEBUG = True
DEBUG_DIR = "debug_output"

def debug_print(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

def save_debug_html(content, filename):
    if DEBUG:
        os.makedirs(DEBUG_DIR, exist_ok=True)
        path = os.path.join(DEBUG_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        debug_print(f"HTML 저장: {path}")

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
    soup = BeautifulSoup(html, "html.parser")

    # 1) data-lb-trigger가 /p/intentblock 또는 /p/ugc로 시작하는 앵커
    for prefix in ['/p/intentblock', '/p/ugc']:
        a = soup.select_one(f'a[data-lb-trigger^="{prefix}"]')
        if a:
            debug_print(f"더보기 발견 (data-lb-trigger): {a.get('data-lb-trigger')[:80]}")
            return {
                "found": True,
                "title": "인기글",
                "more_url": a.get("data-lb-trigger"),
                "referer": search_url
            }

    # 2) href가 /p/intentblock 또는 /p/ugc로 시작
    for prefix in ['/p/intentblock', '/p/ugc']:
        a = soup.select_one(f'a[href^="{prefix}"]')
        if a:
            debug_print(f"더보기 발견 (href): {a.get('href')[:80]}")
            return {
                "found": True,
                "title": "인기글",
                "more_url": a.get("href"),
                "referer": search_url
            }

    # 3) '인기글' 텍스트 기준
    for el in soup.find_all(string=lambda t: t and "인기글" in t):
        blk = None
        for parent in (el.parent, el.parent and el.parent.parent):
            if getattr(parent, "name", None):
                blk = parent
                break
        ctx = blk or soup

        for s in ctx.find_all("span"):
            if s.string and "더보기" in s.string:
                a = s.find_parent("a")
                if a and (a.get("data-lb-trigger") or a.get("href")):
                    more = a.get("data-lb-trigger") or a.get("href")
                    if more and more != "#" and ("/intentblock" in more or "/ugc" in more):
                        debug_print(f"더보기 발견 (더보기 버튼): {more[:80]}")
                        return {
                            "found": True,
                            "title": "인기글",
                            "more_url": more,
                            "referer": search_url
                        }

        # data-lb-trigger가 있는 앵커 중 intentblock이나 ugc 포함
        for a in ctx.find_all("a", attrs={"data-lb-trigger": True}):
            trigger = a.get("data-lb-trigger", "")
            if "/intentblock" in trigger or "/ugc" in trigger:
                debug_print(f"더보기 발견 (data-lb-trigger 검색): {trigger[:80]}")
                return {
                    "found": True,
                    "title": "인기글",
                    "more_url": trigger,
                    "referer": search_url
                }

    # 4) 정규식 - intentblock 또는 ugc를 포함하는 URL만
    m = re.search(r'["\'](/p/(?:intentblock|ugc)/[^"\']+)["\']', html)
    if m:
        debug_print(f"더보기 발견 (정규식): {m.group(1)[:80]}")
        return {
            "found": True,
            "title": "인기글",
            "more_url": m.group(1),
            "referer": search_url
        }

    # 5) 더 관대한 정규식 - 긴 URL만 (최소 30자)
    m = re.search(r'["\'](/p/[^"\']{30,})["\']', html)
    if m:
        debug_print(f"더보기 발견 (긴 URL): {m.group(1)[:80]}")
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
        if url.startswith("/p/"):
            full = "https://s.search.naver.com" + url
        else:
            full = "https://search.naver.com" + url

    debug_print(f"더보기 요청: {full}")
    r = req_get(full, headers={"Referer": referer or "https://search.naver.com/"})

    if r.status_code != 200:
        debug_print(f"더보기 실패: {r.status_code}")
        return None

    debug_print(f"응답 Content-Type: {r.headers.get('Content-Type')}")

    # JSON 응답 처리
    try:
        j = r.json()
        debug_print("JSON 응답 감지")
        html_content = ""

        if "dom" in j:
            debug_print(f"'dom' 키 발견")
            if "collection" in j["dom"]:
                debug_print(f"collection 개수: {len(j['dom']['collection'])}")
                for idx, item in enumerate(j["dom"]["collection"]):
                    if "html" in item:
                        decoded = html_module.unescape(item["html"])
                        html_content += decoded
                        debug_print(f"  아이템 {idx}: HTML 길이 {len(decoded)}")

        if html_content:
            debug_print(f"총 HTML 길이: {len(html_content)}")
            return html_content
        else:
            debug_print("JSON에서 HTML 추출 실패, 원본 반환")
            return r.text
    except Exception as e:
        debug_print(f"JSON 파싱 실패: {e}, HTML로 처리")
        return r.text

def find_cafe_posts_in_top20(html):
    """
    개선된 카페 글 추출 - 더 견고한 로직
    """
    debug_print("\n=== 카페 글 추출 시작 ===")
    save_debug_html(html, "more_page.html")

    soup = BeautifulSoup(html, "html.parser")

    # 방법1: 정확한 선택자 사용
    cafe_links1 = soup.select('a[href*="cafe.naver.com"]')
    debug_print(f"방법1 (select): {len(cafe_links1)}개 링크")

    # 방법2: find_all with lambda
    cafe_links2 = soup.find_all('a', href=lambda h: h and 'cafe.naver.com' in h)
    debug_print(f"방법2 (find_all): {len(cafe_links2)}개 링크")

    # 방법3: 정규식으로 HTML에서 직접 찾기
    pattern = r'href=["\']([^"\']*cafe\.naver\.com[^"\']*)["\']'
    direct_links = re.findall(pattern, html)
    debug_print(f"방법3 (정규식): {len(direct_links)}개 링크")

    # 가장 많이 찾은 방법 사용
    if direct_links:
        debug_print("정규식 방법 사용")
        return extract_from_regex_links(html, direct_links)
    elif cafe_links2:
        debug_print("find_all 방법 사용")
        return extract_from_soup_links(soup, cafe_links2)
    elif cafe_links1:
        debug_print("select 방법 사용")
        return extract_from_soup_links(soup, cafe_links1)
    else:
        debug_print("카페 링크를 찾을 수 없음!")
        # HTML 샘플 출력
        debug_print(f"HTML 샘플 (처음 500자):\n{html[:500]}")
        return []

def extract_from_regex_links(html, links):
    """정규식으로 찾은 링크에서 정보 추출"""
    soup = BeautifulSoup(html, "html.parser")
    results = []
    seen = set()

    for link_url in links[:30]:
        if link_url in seen:
            continue
        seen.add(link_url)

        # 해당 링크를 가진 a 태그 찾기
        link_elem = soup.find('a', href=link_url)
        if not link_elem:
            continue

        # 제목 추출
        title = link_elem.get_text(strip=True)

        # 부모 컨테이너 찾기
        container = find_container(link_elem)

        # 카페명 추출
        cafe_name = extract_cafe_name(container, link_url)

        # 카페 ID 추출
        cafe_id = extract_cafe_id(link_url)

        results.append({
            "rank": len(results) + 1,
            "title": title[:100] if title else "제목 없음",
            "cafe_name": cafe_name,
            "cafe_id": cafe_id,
            "url": link_url
        })

        debug_print(f"  {len(results)}. [{cafe_name}] {title[:40]}")

        if len(results) >= 20:
            break

    return results

def extract_from_soup_links(soup, links):
    """BeautifulSoup으로 찾은 링크에서 정보 추출"""
    results = []
    seen = set()

    for link in links:
        url = link.get('href', '')
        if not url or url in seen:
            continue
        seen.add(url)

        # 제목 추출
        title = link.get_text(strip=True)

        # 부모 컨테이너 찾기
        container = find_container(link)

        # 카페명 추출
        cafe_name = extract_cafe_name(container, url)

        # 카페 ID 추출
        cafe_id = extract_cafe_id(url)

        results.append({
            "rank": len(results) + 1,
            "title": title[:100] if title else "제목 없음",
            "cafe_name": cafe_name,
            "cafe_id": cafe_id,
            "url": url
        })

        debug_print(f"  {len(results)}. [{cafe_name}] {title[:40]}")

        if len(results) >= 20:
            break

    return results

def find_container(element):
    """요소의 부모 컨테이너 찾기"""
    current = element
    for _ in range(10):
        if not current or not hasattr(current, 'parent'):
            break
        current = current.parent
        if current and hasattr(current, 'name'):
            if current.name in ['li', 'div', 'article'] and current.get('class'):
                return current
    return element.parent if element and hasattr(element, 'parent') else None

def extract_cafe_name(container, url):
    """카페명 추출 - 여러 방법 시도"""
    if container:
        # 전체 텍스트에서 매핑 찾기
        text = container.get_text(" ", strip=True)
        for keyword, simple_name in CAFE_NAME_MAPPING.items():
            if keyword in text:
                return simple_name

        # 특정 요소에서 찾기
        for selector in ['[class*="source"]', '[class*="name"]', '[class*="cafe"]',
                        '[class*="writer"]', 'em', 'span', 'div']:
            elem = container.select_one(selector)
            if elem:
                elem_text = elem.get_text(strip=True)
                for keyword, simple_name in CAFE_NAME_MAPPING.items():
                    if keyword in elem_text:
                        return simple_name

    # URL에서 카페 ID 추출
    return extract_cafe_id(url)

def extract_cafe_id(url):
    """URL에서 카페 ID 추출"""
    try:
        if 'cafe.naver.com/' in url:
            parts = url.split('cafe.naver.com/')[1].split('/')[0].split('?')[0]
            return parts
    except:
        pass
    return "알 수 없음"

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
        debug_print(f"\n{'='*50}")
        debug_print(f"키워드: {keyword}")
        debug_print(f"{'='*50}")

        html, search_url = search_naver(keyword)
        if not html:
            result["error"] = "검색 실패"
            return result

        save_debug_html(html, f"search_{keyword}.html")
        time.sleep(random.uniform(1, 2))

        section = find_popular_posts_section(html, search_url)
        if not section.get("found"):
            result["error"] = "인기글 섹션 없음"
            return result
        result["has_popular_section"] = True
        debug_print(f"더보기 URL: {section.get('more_url')}")

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
            debug_print(f"총 {len(cafe_posts)}개 카페 글 추출 완료")
        else:
            result["error"] = "카페 글 없음"
            debug_print("카페 글을 찾을 수 없음!")

        return result
    except Exception as e:
        result["error"] = f"오류: {e}"
        if DEBUG:
            import traceback
            traceback.print_exc()
        return result

def save_to_excel(results, output_path):
    df = pd.DataFrame(results)
    df.to_excel(output_path, index=False, engine="openpyxl")

def main():
    print("="*60)
    print("카페 크롤러 (디버그 모드)")
    print("="*60)

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
        print(f"\n[{i}/{n}] {kw} | " + " | ".join(status) + f" | 오류:{err}")

        if i < n:
            time.sleep(random.uniform(3, 5))

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(current_dir, f"크롤링_결과_{ts}.xlsx")
    save_to_excel(all_results, out)

    # 최종 요약
    has_pop = sum(1 for r in all_results if r["has_popular_section"])
    has_more = sum(1 for r in all_results if r["has_more_button"])
    has_cafe = sum(1 for r in all_results if r["cafe_count"] > 0)
    print(f"\n{'='*60}")
    print(f"총:{len(all_results)} | 인기글:{has_pop} | 더보기:{has_more} | 카페≥1:{has_cafe}")
    print(f"파일:{out}")
    print(f"디버그 HTML 저장 위치: {DEBUG_DIR}/")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
