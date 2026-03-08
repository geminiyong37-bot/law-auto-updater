import os
import requests
import xml.etree.ElementTree as ET

OC_ID = os.environ.get("LAW_API_KEY")
SEARCH_URL = "http://www.law.go.kr/DRF/lawSearch.do"
SERVICE_URL = "http://www.law.go.kr/DRF/lawService.do"

# --- [1] 법령(법, 시행령, 시행규칙 등) 목록 ---
LAWS_TO_FETCH = {
    "사립대학": ["사립학교법", "사립학교법 시행령", "사학기관 재무·회계 규칙", "사학기관 재무·회계 규칙에 대한 특례규칙", "대학설립·운영 규정", "대학설립·운영 규정 시행규칙", "사이버대학 설립·운영 규정", "대학 등록금에 관한 규칙"],
    "평생교육": ["평생교육법", "평생교육법 시행령", "평생교육법 시행규칙"],
    "부속병원": ["의료기관 회계기준 규칙"],
    "산학협력단": ["산업교육진흥 및 산학연협력촉진에 관한 법률", "산업교육진흥 및 산학연협력촉진에 관한 법률 시행령", "산업교육진흥 및 산학연협력촉진에 관한 법률 시행규칙", "국가연구개발혁신법", "국가연구개발혁신법 시행령", "국가연구개발혁신법 시행규칙"],
    "재외교육기관": ["재외국민의 교육지원 등에 관한 법률", "재외국민의 교육지원 등에 관한 법률 시행령", "재외국민의 교육지원 등에 관한 법률 시행규칙"],
    "세법": [
        "법인세법", "법인세법 시행령", "법인세법 시행규칙",
        "상속세 및 증여세법", "상속세 및 증여세법 시행령", "상속세 및 증여세법 시행규칙",
        "부가가치세법", "부가가치세법 시행령", "부가가치세법 시행규칙",
        "소득세법", "소득세법 시행령", "소득세법 시행규칙",
        "사립학교교직원 연금법", "사립학교교직원 연금법 시행령",
        "근로자퇴직급여 보장법", "근로자퇴직급여 보장법 시행령",
        "공익법인의 설립ㆍ운영에 관한 법률", "공익법인의 설립ㆍ운영에 관한 법률 시행령",
        "지방세법", "지방세법 시행령", "지방세법 시행규칙"
    ]
}

# --- [2] 행정규칙(고시, 훈령, 예규 등) 목록 ---
ADMIN_RULES_TO_FETCH = {
    "사립대학": ["사학기관 외부회계감사 유의사항", "사학기관 외부회계감사 감리에 관한 고시", "사학기관 외부감사인 지정 등에 관한 고시"],
    "학교기업": ["학교기업 회계처리규칙"],
    "평생교육": ["평생교육법", "평생교육법 시행령", "평생교육법 시행규칙"],
    "부속병원": ["재무제표 세부 작성방법"],
    "산학협력단": ["산학협력단회계처리규칙", "국가연구개발사업 연구개발비 사용 기준", "산학연협력기술지주회사 설립절차 등에 관한 규정", "계약학과 설치·운영 규정", "국가연구개발 시설·장비의 관리 등에 관한 표준지침"],
    "재외교육기관": ["재외공관 비소모품 관리규정"],
    "기본재산": ["교육용 기본재산 처분에 대한 기준 고시"]
}

def fetch_law_body():
    """기존 법령 수집 함수 (target=law)"""
    for category, law_names in LAWS_TO_FETCH.items():
        path = f"laws/{category}"
        os.makedirs(path, exist_ok=True)
        
        for name in law_names:
            print(f"📘 [법령 - {category}] {name} 수집 중...")
            params = {"OC": OC_ID, "target": "law", "query": name, "type": "XML"}
            try:
                search_res = requests.get(SEARCH_URL, params=params)
                mst = ET.fromstring(search_res.content).findtext(".//법령일련번호")
                if not mst: 
                    print(f"  └ ⚠️ '{name}'의 법령일련번호를 찾을 수 없음.")
                    continue

                params_body = {"OC": OC_ID, "target": "law", "MST": mst, "type": "XML"}
                response = requests.get(SERVICE_URL, params=params_body)
                root = ET.fromstring(response.content)

                # 파일명 치환 규칙: 공백, 가운뎃점(·), 아래아 가운뎃점(ㆍ) 모두 언더바로 변경
                file_name = name.replace(" ", "_").replace("·", "_").replace("ㆍ", "_")
                
                with open(f"{path}/{file_name}.md", "w", encoding="utf-8") as f:
                    f.write(f"# {name}\n\n")
                    f.write("## 📜 조문 본문\n")
                    for jo in root.findall(".//조문단위"):
                        title = jo.findtext("조문내용", "")
                        f.write(f"### {title}\n")
                        for hang in jo.findall(".//항내용"):
                            if hang.text: f.write(f"{hang.text}\n")
                        f.write("\n")
                    
                    f.write("\n---\n## 📎 별표 및 서식 내용\n")
                    bylpyo_list = root.findall(".//별표단위")
                    if bylpyo_list:
                        for bp in bylpyo_list:
                            bp_title = bp.findtext("별표제목", "제목 없음")
                            bp_content = bp.findtext("별표내용", "")
                            f.write(f"### 📄 {bp_title}\n")
                            if bp_content:
                                f.write(f"{bp_content}\n")
                            else:
                                f.write("> (텍스트 데이터가 없습니다.)\n")
                            f.write("\n")
                    else:
                        f.write("해당 법령에는 별표 데이터가 없습니다.\n")
                print(f"  └ ✅ 완료: {path}/{file_name}.md")
            except Exception as e:
                print(f"  └ ❗ 실패 ({name}): {e}")

def fetch_admrul_body():
    """행정규칙(고시) 수집 함수 (target=admrul)"""
    for category, rule_names in ADMIN_RULES_TO_FETCH.items():
        path = f"laws/{category}"
        os.makedirs(path, exist_ok=True)
        
        for name in rule_names:
            print(f"📙 [고시 - {category}] {name} 수집 중...")
            params = {"OC": OC_ID, "target": "admrul", "query": name, "type": "XML"}
            try:
                search_res = requests.get(SEARCH_URL, params=params)
                amrst = ET.fromstring(search_res.content).findtext(".//행정규칙일련번호")
                if not amrst: 
                    print(f"  └ ⚠️ '{name}'의 행정규칙일련번호를 찾을 수 없음.")
                    continue

                params_body = {"OC": OC_ID, "target": "admrul", "AMRST": amrst, "type": "XML"}
                response = requests.get(SERVICE_URL, params=params_body)
                root = ET.fromstring(response.content)

                # 파일명 치환 규칙 통일
                file_name = name.replace(" ", "_").replace("·", "_").replace("ㆍ", "_")
                
                with open(f"{path}/{file_name}.md", "w", encoding="utf-8") as f:
                    f.write(f"# {name}\n\n")
                    f.write("## 📜 규칙 본문\n")
                    jo_list = root.findall(".//조문단위")
                    
                    if jo_list:
                        for jo in jo_list:
                            title = jo.findtext("조문내용", "")
                            f.write(f"### {title}\n")
                            for hang in jo.findall(".//항내용"):
                                if hang.text: f.write(f"{hang.text}\n")
                            f.write("\n")
                    else:
                        content = root.findtext(".//행정규칙내용", "")
                        if content:
                            f.write(f"{content}\n\n")
                        else:
                            f.write("본문 텍스트를 파싱할 수 없습니다.\n\n")

                    f.write("\n---\n## 📎 별표 및 서식 내용\n")
                    bylpyo_list = root.findall(".//별표단위")
                    if bylpyo_list:
                        for bp in bylpyo_list:
                            bp_title = bp.findtext("별표제목", "제목 없음")
                            bp_content = bp.findtext("별표내용", "")
                            f.write(f"### 📄 {bp_title}\n")
                            if bp_content:
                                f.write(f"{bp_content}\n")
                            else:
                                f.write("> (텍스트 데이터가 없습니다.)\n")
                            f.write("\n")
                    else:
                        f.write("해당 고시에는 별표 데이터가 없습니다.\n")
                print(f"  └ ✅ 완료: {path}/{file_name}.md")
            except Exception as e:
                print(f"  └ ❗ 실패 ({name}): {e}")

if __name__ == "__main__":
    print("🚀 국가법령정보 수집 스크립트 시작\n")
    fetch_law_body()
    print("-" * 40)
    fetch_admrul_body()
    print("\n✅ 모든 데이터 수집 및 업데이트 완료!")
