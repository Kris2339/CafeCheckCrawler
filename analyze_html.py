import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def analyze_search_page(keyword):
    """네이버 검색 페이지를 분석하여 실제 HTML 구조를 확인"""

    url = f"https://search.naver.com/search.naver?query={quote(keyword)}"
    print(f"검색 URL: {url}\n")

    try:
        headers = {
            "User-Agent": UA,
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        }
        r = requests.get(url, headers=headers, timeout=10)
        print(f"응답 상태: {r.status_code}\n")

        if r.status_code != 200:
            print(f"에러: {r.status_code}")
            return

        html = r.text
        soup = BeautifulSoup(html, 'html.parser')

        # 1. '인기글' 텍스트 찾기
        print("="*60)
        print("1. '인기글' 텍스트 검색")
        print("="*60)

        popular_texts = soup.find_all(string=lambda t: t and "인기글" in t)
        if popular_texts:
            print(f"발견: {len(popular_texts)}개")
            for i, text in enumerate(popular_texts[:3], 1):
                print(f"\n[{i}] 텍스트: {text.strip()}")
                parent = text.parent
                if parent:
                    print(f"    부모 태그: <{parent.name}> class={parent.get('class', [])}")
                    print(f"    부모 HTML (처음 200자):\n    {str(parent)[:200]}")
        else:
            print("❌ '인기글' 텍스트 없음")

        # 2. '더보기' 링크 찾기
        print("\n" + "="*60)
        print("2. '더보기' 링크 검색")
        print("="*60)

        more_links = soup.find_all('a', string=lambda t: t and "더보기" in t)
        if not more_links:
            more_links = soup.find_all('a', text=re.compile("더보기"))

        if more_links:
            print(f"발견: {len(more_links)}개")
            for i, link in enumerate(more_links[:5], 1):
                print(f"\n[{i}] 텍스트: {link.get_text(strip=True)}")
                print(f"    href: {link.get('href', 'None')}")
                print(f"    data-lb-trigger: {link.get('data-lb-trigger', 'None')}")
                print(f"    class: {link.get('class', [])}")
        else:
            print("❌ '더보기' 링크 없음")

        # 3. data-lb-trigger 속성 찾기
        print("\n" + "="*60)
        print("3. data-lb-trigger 속성 검색")
        print("="*60)

        triggers = soup.find_all(attrs={"data-lb-trigger": True})
        if triggers:
            print(f"발견: {len(triggers)}개")
            for i, elem in enumerate(triggers[:10], 1):
                trigger_val = elem.get('data-lb-trigger', '')
                print(f"\n[{i}] <{elem.name}> trigger: {trigger_val[:80]}")
        else:
            print("❌ data-lb-trigger 없음")

        # 4. /p/ 로 시작하는 URL 정규식 검색
        print("\n" + "="*60)
        print("4. /p/ URL 패턴 검색 (정규식)")
        print("="*60)

        patterns = [
            (r'["\'](/p/intentblock[^"\']+)["\']', '/p/intentblock'),
            (r'["\'](/p/ugc[^"\']+)["\']', '/p/ugc'),
            (r'["\'](/p/[^"\']{30,})["\']', '/p/... (긴 URL)'),
            (r'["\'](/p/[^"\']+)["\']', '/p/... (모든 URL)')
        ]

        for pattern, desc in patterns:
            matches = re.findall(pattern, html)
            print(f"\n{desc}: {len(matches)}개")
            if matches:
                for i, match in enumerate(matches[:3], 1):
                    print(f"  [{i}] {match[:100]}")

        # 5. cafe.naver.com 링크 찾기
        print("\n" + "="*60)
        print("5. cafe.naver.com 링크 검색")
        print("="*60)

        cafe_links = soup.find_all('a', href=lambda h: h and 'cafe.naver.com' in h)
        print(f"발견: {len(cafe_links)}개")

        if cafe_links:
            for i, link in enumerate(cafe_links[:5], 1):
                print(f"\n[{i}] 텍스트: {link.get_text(strip=True)[:50]}")
                print(f"    URL: {link.get('href', '')[:80]}")
                print(f"    class: {link.get('class', [])}")

        # 6. HTML 샘플 저장
        print("\n" + "="*60)
        print("6. HTML 저장")
        print("="*60)

        filename = f"analysis_{keyword}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"저장됨: {filename}")
        print(f"파일 크기: {len(html)} bytes")

        # 7. 특정 키워드로 HTML 검색
        print("\n" + "="*60)
        print("7. HTML 내 주요 키워드 검색")
        print("="*60)

        keywords_to_find = ['인기글', '더보기', 'ugc', 'intentblock', 'cafe.naver.com']
        for kw in keywords_to_find:
            count = html.count(kw)
            print(f"{kw}: {count}회 출현")

    except Exception as e:
        print(f"에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    keyword = input("검색할 키워드 입력 (엔터=당뇨에좋은음식): ").strip()
    if not keyword:
        keyword = "당뇨에좋은음식"

    print("\n" + "="*60)
    print(f"키워드: {keyword}")
    print("="*60 + "\n")

    analyze_search_page(keyword)
