import os
import requests
import xml.etree.ElementTree as ET

# GitHub Secrets에서 가져온 내 아이디(OC)
OC_ID = os.environ.get("LAW_API_KEY") 
BASE_URL = "http://www.law.go.kr/DRF/lawService.do"

# 2026년 기준 MST 번호 (하위법령을 기본법 카테고리로 통합)
LAWS_TO_FETCH = {
    "기본법": {
        "사립학교법": "233816",
        "사립학교법 시행령": "259344",
        "사립학교법 시행규칙": "250462"
    },
    "회계규칙": {
        "사학기관 재무·회계 규칙": "253503",
        "사학기관 재무·회계 규칙에 대한 특례규칙": "249845",
        "학교기업 회계처리 규칙": "210411"
    }
}

def fetch_law_and_save():
    if not OC_ID:
        print("에러: LAW_API_KEY(OC ID)가 설정되지 않았어!")
        return

    for category, laws in LAWS_TO_FETCH.items():
        for law_name, mst in laws.items():
            params = {
                "OC": OC_ID,
                "target": "law",
                "MST": mst,
                "type": "XML"
            }
            try:
                response = requests.get(BASE_URL, params=params)
                if "일치하는 법령이 없습니다" in response.text:
                    print(f"주의: {law_name}(MST:{mst})을 찾을 수 없어.")
                    continue

                if response.status_code == 200:
                    path = f"laws/{category}"
                    os.makedirs(path, exist_ok=True)
                    
                    root = ET.fromstring(response.content)
                    filename = f"{path}/{law_name}.md"
                    
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(f"# {law_name}\n\n")
                        for jo in root.findall(".//조문단위"):
                            title = jo.findtext("조문내용", "")
                            f.write(f"## {title}\n")
                            for hang in jo.findall(".//항내용"):
                                if hang.text: f.write(f"{hang.text}\n")
                            f.write("\n")
                    print(f"성공: {law_name}")
            except Exception as e:
                print(f"에러 발생({law_name}): {e}")

if __name__ == "__main__":
    fetch_law_and_save()
