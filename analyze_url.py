import requests
from bs4 import BeautifulSoup
import json

url = "https://s.search.naver.com/p/intentblock/35/search.naver?ac=0&aq=0&bid=SYS-0000000006025584&display=10&lgl_lat=37.495484&lgl_long=127.033357&lgl_rcode=09680101&ngn_country=KR&nlu_query=%7B%22nquery%22%3A%22%EB%8B%B9%EB%87%A8%EC%97%90%EC%A2%8B%EC%9D%80%EC%9D%8C%EC%8B%9D%22%2C%22concept%22%3A%5B%7B%22text%22%3A%22%EB%8B%B9%EB%87%A8%22%2C%22fps%22%3A0%2C%22lps%22%3A5%7D%2C%7B%22text%22%3A%22%EC%97%90%22%2C%22fps%22%3A6%2C%22lps%22%3A8%2C%22josa%22%3Atrue%7D%2C%7B%22text%22%3A%22%EC%A2%8B%EC%9D%80%22%2C%22fps%22%3A9%2C%22lps%22%3A14%2C%22predicate%22%3Atrue%7D%2C%7B%22text%22%3A%22%EC%A2%8B%EC%9D%80%EC%9D%8C%EC%8B%9D%22%2C%22fps%22%3A9%2C%22lps%22%3A20%7D%2C%7B%22text%22%3A%22%EC%9D%8C%EC%8B%9D%22%2C%22fps%22%3A15%2C%22lps%22%3A20%7D%5D%2C%22query-form%22%3A4%7D&query=%EB%8B%B9%EB%87%A8%EC%97%90%EC%A2%8B%EC%9D%80%EC%9D%8C%EC%8B%9D&sm=&ssc=tab.itb.all&start=1&where=nx_bridge_more_fender_api"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/html",
    "Referer": "https://search.naver.com/"
}

try:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"상태 코드: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type', 'Unknown')}")
    print(f"응답 길이: {len(r.text)}")
    print()

    # JSON 응답인지 확인
    if 'application/json' in r.headers.get('Content-Type', ''):
        try:
            data = r.json()
            print("JSON 응답입니다!")
            print(f"JSON 키: {list(data.keys())}")

            # HTML 추출 시도
            if 'dom' in data:
                print("\n'dom' 키 발견!")
                if 'collection' in data['dom']:
                    print(f"collection 개수: {len(data['dom']['collection'])}")

                    html_parts = []
                    for i, item in enumerate(data['dom']['collection']):
                        if 'html' in item:
                            import html as html_module
                            html_content = html_module.unescape(item['html'])
                            html_parts.append(html_content)
                            print(f"  아이템 {i}: HTML 길이 {len(html_content)}")

                    if html_parts:
                        full_html = ''.join(html_parts)
                        print(f"\n전체 HTML 길이: {len(full_html)}")

                        # HTML 파싱
                        soup = BeautifulSoup(full_html, 'html.parser')

                        # cafe.naver.com 링크 찾기
                        cafe_links = soup.find_all('a', href=lambda h: h and 'cafe.naver.com' in h)
                        print(f"\n카페 링크 개수: {len(cafe_links)}")

                        if cafe_links:
                            print("\n첫 5개 링크 분석:")
                            for i, link in enumerate(cafe_links[:5], 1):
                                print(f"\n링크 {i}:")
                                print(f"  href: {link.get('href', '')[:80]}")
                                print(f"  텍스트: {link.get_text(strip=True)[:80]}")
                                print(f"  클래스: {link.get('class', [])}")

                                # 부모 요소 분석
                                parent = link.parent
                                for level in range(5):
                                    if parent:
                                        classes = ' '.join(parent.get('class', []))
                                        print(f"  부모{level+1} <{parent.name}> class={classes[:50]}")
                                        parent = parent.parent

                        # HTML 저장
                        with open('analyzed.html', 'w', encoding='utf-8') as f:
                            f.write(full_html)
                        print("\nHTML 저장: analyzed.html")
        except json.JSONDecodeError:
            print("JSON 파싱 실패, HTML로 처리")
            soup = BeautifulSoup(r.text, 'html.parser')
            cafe_links = soup.find_all('a', href=lambda h: h and 'cafe.naver.com' in h)
            print(f"카페 링크 개수: {len(cafe_links)}")
    else:
        # HTML 응답
        soup = BeautifulSoup(r.text, 'html.parser')
        cafe_links = soup.find_all('a', href=lambda h: h and 'cafe.naver.com' in h)
        print(f"카페 링크 개수: {len(cafe_links)}")

        with open('analyzed.html', 'w', encoding='utf-8') as f:
            f.write(r.text)
        print("HTML 저장: analyzed.html")

except Exception as e:
    print(f"에러: {e}")
    import traceback
    traceback.print_exc()
