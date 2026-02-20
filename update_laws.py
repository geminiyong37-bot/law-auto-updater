import os
import requests
import xml.etree.ElementTree as ET

OC_ID = os.environ.get("LAW_API_KEY")
SEARCH_URL = "http://www.law.go.kr/DRF/lawSearch.do"
SERVICE_URL = "http://www.law.go.kr/DRF/lawService.do"

LAWS_TO_FETCH = {
    "기본법": ["사립학교법", "사립학교법 시행령", "사립학교법 시행규칙"],
    "회계규칙": ["사학기관 재무·회계 규칙", "사학기관 재무·회계 규칙에 대한 특례규칙", "학교기업 회계처리규칙"]
}

def fetch_law_body():
    for category, law_names in LAWS_TO_FETCH.items():
        path = f"laws/{category}"
        os.makedirs(path, exist_ok=True)
        
        for name in law_names:
            # 1. MST 조회
            params = {"OC": OC_ID, "target": "law", "query": name, "type": "XML"}
            try:
                search_res = requests.get(SEARCH_URL, params=params)
                mst = ET.fromstring(search_res.content).findtext(".//법령일련번호")
                if not mst:
                    print(f"⚠️ MST 못 찾음: {name}")
                    continue

                # 2. 본문 수집
                params_body = {"OC": OC_ID, "target": "law", "MST": mst, "type": "XML"}
                response = requests.get(SERVICE_URL, params=params_body)
                root = ET.fromstring(response.content)

                # 3. 파일 저장
                with open(f"{path}/{name}.md", "w", encoding="utf-8") as f:
                    f.write(f"# {name}\n\n")
                    for jo in root.findall(".//조문단위"):
                        title = jo.findtext("조문내용", "")
                        f.write(f"## {title}\n")
                        for hang in jo.findall(".//항내용"):
                            if hang.text: f.write(f"{hang.text}\n")
                        f.write("\n")
                print(f"✅ 다운로드 성공: {name}")
            except Exception as e:
                print(f"❗ 실패 ({name}): {e}")

if __name__ == "__main__":
    fetch_law_body()
