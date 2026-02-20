import os
import requests
import xml.etree.ElementTree as ET

OC_ID = os.environ.get("LAW_API_KEY")
SEARCH_URL = "http://www.law.go.kr/DRF/lawSearch.do"
SERVICE_URL = "http://www.law.go.kr/DRF/lawService.do"

# 폴더별 법령 목록
LAWS_TO_FETCH = {
    "기본법": ["사립학교법", "사립학교법 시행령", "사립학교법 시행규칙"],
    "회계규칙": ["사학기관 재무·회계 규칙", "사학기관 재무·회계 규칙에 대한 특례규칙", "학교기업 회계처리규칙"]
}

def fetch_law_body():
    for category, law_names in LAWS_TO_FETCH.items():
        path = f"laws/{category}"
        os.makedirs(path, exist_ok=True)
        
        for name in law_names:
            print(f"[{category}] {name} 본문 및 별표 텍스트 수집 중...")
            params = {"OC": OC_ID, "target": "law", "query": name, "type": "XML"}
            try:
                # 1. MST 조회
                search_res = requests.get(SEARCH_URL, params=params)
                mst = ET.fromstring(search_res.content).findtext(".//법령일련번호")
                if not mst: continue

                # 2. 본문 및 별표 데이터 수집
                params_body = {"OC": OC_ID, "target": "law", "MST": mst, "type": "XML"}
                response = requests.get(SERVICE_URL, params=params_body)
                root = ET.fromstring(response.content)

                # 3. 파일 저장 (공백/특수문자 처리)
                file_name = name.replace("·", "_").replace(" ", "_")
                with open(f"{path}/{file_name}.md", "w", encoding="utf-8") as f:
                    f.write(f"# {name}\n\n")
                    
                    # --- [1] 조문 본문 수집 ---
                    f.write("## 📜 조문 본문\n")
                    for jo in root.findall(".//조문단위"):
                        title = jo.findtext("조문내용", "")
                        f.write(f"### {title}\n")
                        for hang in jo.findall(".//항내용"):
                            if hang.text: f.write(f"{hang.text}\n")
                        f.write("\n")
                    
                    # --- [2] 별표 및 서식 텍스트 수집 (링크 제외 버전) ---
                    f.write("\n---\n## 📎 별표 및 서식 내용\n")
                    bylpyo_list = root.findall(".//별표단위")
                    
                    if bylpyo_list:
                        for bp in bylpyo_list:
                            bp_title = bp.findtext("별표제목", "제목 없음")
                            bp_content = bp.findtext("별표내용", "") # 별표의 실제 텍스트 내용
                            
                            f.write(f"### 📄 {bp_title}\n")
                            if bp_content:
                                f.write(f"{bp_content}\n")
                            else:
                                f.write("> (해당 별표는 이미지 또는 복잡한 서식으로 구성되어 텍스트 데이터가 없습니다.)\n")
                            f.write("\n")
                    else:
                        f.write("해당 법령에는 별표 또는 서식 데이터가 없습니다.\n")

                print(f"✅ 성공: {path}/{file_name}.md")
            except Exception as e:
                print(f"❗ 실패 ({name}): {e}")

if __name__ == "__main__":
    fetch_law_body()
