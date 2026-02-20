import os
import requests
import xml.etree.ElementTree as ET

OC_ID = os.environ.get("LAW_API_KEY")
# 가이드에 나온 두 가지 API 주소
SEARCH_URL = "http://www.law.go.kr/DRF/lawSearch.do" # 번호 찾기용
SERVICE_URL = "http://www.law.go.kr/DRF/lawService.do" # 본문 가져오기용

# 이제 번호(MST) 대신 이름만 적어줘!
LAWS_TO_FETCH = {
    "기본법": ["사립학교법", "사립학교법 시행령", "사립학교법 시행규칙"],
    "회계규칙": ["사학기관 재무·회계 규칙", "사학기관 재무·회계 규칙에 대한 특례규칙", "학교기업 회계처리 규칙"]
}

def get_latest_mst(law_name):
    """법령 이름으로 최신 MST 번호를 조회함"""
    params = {
        "OC": OC_ID,
        "target": "law",
        "query": law_name,
        "type": "XML"
    }
    response = requests.get(SEARCH_URL, params=params)
    root = ET.fromstring(response.content)
    # 검색 결과 중 가장 첫 번째(최신) 법령의 MST를 반환
    mst = root.findtext(".//법령일련번호")
    return mst

def fetch_all_laws():
    for category, law_list in LAWS_TO_FETCH.items():
        for law_name in law_list:
            # 실시간으로 번호를 알아내기 때문에 개정되어도 문제없음!
            mst = get_latest_mst(law_name) 
            if not mst: continue
            
            # 이후 본문을 가져오는 로직은 동일
            params = {"OC": OC_ID, "target": "law", "MST": mst, "type": "XML"}
            # ... (본문 저장 로직 생략)
            print(f"최신 버전 확인 및 저장 완료: {law_name} (MST: {mst})")

if __name__ == "__main__":
    fetch_all_laws()
