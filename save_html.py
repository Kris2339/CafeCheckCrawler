import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import html as html_module
import re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def req_get(url, headers=None):
    h = {
        "User-Agent": UA,
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
    }
    if headers:
        h.update(headers)
    return requests.get(url, headers=h, timeout=10)

def search_and_save(keyword):
    # 1. 검색
    url = f"https://search.naver.com/search.naver?query={quote(keyword)}"
    r = req_get(url)
    print(f"검색 상태: {r.status_code}")

    # 검색 페이지 저장
    with open(f"{keyword}_search.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print(f"검색 페이지 저장: {keyword}_search.html")

    # 2. 인기글 더보기 URL 찾기
    soup = BeautifulSoup(r.text, "html.parser")

    # 방법1: data-lb-trigger
    a = soup.select_one('a[data-lb-trigger^="/p/ugc"]')
    if a:
        more_url = a.get("data-lb-trigger")
        print(f"더보기 URL 발견 (방법1): {more_url}")
    else:
        # 방법2: 정규식
        m = re.search(r'["\'](/p/ugc[^"\']+)["\']', r.text)
        if m:
            more_url = m.group(1)
            print(f"더보기 URL 발견 (방법2): {more_url}")
        else:
            print("더보기 URL을 찾을 수 없음!")
            return

    # 3. 더보기 페이지 가져오기
    if more_url.startswith("/p/ugc"):
        full_url = "https://s.search.naver.com" + more_url
    else:
        full_url = "https://search.naver.com" + more_url

    r2 = req_get(full_url, headers={"Referer": url})
    print(f"더보기 페이지 상태: {r2.status_code}")

    # JSON 파싱 시도
    try:
        j = r2.json()
        html_content = ""
        if "dom" in j and "collection" in j["dom"]:
            for item in j["dom"]["collection"]:
                if "html" in item:
                    html_content += html_module.unescape(item["html"])

        if html_content:
            with open(f"{keyword}_more.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"더보기 페이지 저장 (JSON): {keyword}_more.html")
            print(f"HTML 길이: {len(html_content)}")

            # 카페 링크 개수 확인
            soup2 = BeautifulSoup(html_content, "html.parser")
            cafe_links = soup2.select('a[href*="cafe.naver.com"]')
            print(f"카페 링크 개수: {len(cafe_links)}")

            if cafe_links:
                print("\n처음 3개 링크:")
                for i, link in enumerate(cafe_links[:3], 1):
                    print(f"{i}. {link.get('href', '')}")
                    print(f"   텍스트: {link.get_text(strip=True)[:50]}")
        else:
            print("JSON에서 HTML을 추출할 수 없음")
    except Exception as e:
        print(f"JSON 파싱 실패: {e}")
        with open(f"{keyword}_more_raw.html", "w", encoding="utf-8") as f:
            f.write(r2.text)
        print(f"원본 저장: {keyword}_more_raw.html")

if __name__ == "__main__":
    search_and_save("당뇨에좋은음식")
