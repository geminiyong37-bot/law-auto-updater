# 스크립트 상단에 추가
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_gdrive(file_path, folder_id):
    # Secret에서 가져온 JSON 값을 환경변수로 읽음
    info = json.loads(os.environ['GDRIVE_JSON_RAW']) # Base64 안 해도 됨
    creds = service_account.Credentials.from_service_account_info(info)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
import os
import requests
import xml.etree.ElementTree as ET

# GitHub Secrets에서 가져온 사용자 ID(OC)
OC_ID = os.environ.get("LAW_API_KEY") 
SEARCH_URL = "http://www.law.go.kr/DRF/lawSearch.do"
SERVICE_URL = "http://www.law.go.kr/DRF/lawService.do"

# 이제 번호 대신 '이름'만 관리하면 돼!
LAWS_TO_FETCH = {
    "기본법": ["사립학교법", "사립학교법 시행령", "사립학교법 시행규칙"],
    "회계규칙": ["사학기관 재무·회계 규칙", "사학기관 재무·회계 규칙에 대한 특례규칙", "학교기업 회계처리규칙"]
}

def get_latest_mst(law_name):
    """가이드 문서의 lawSearch API를 사용하여 최신 MST를 조회"""
    params = {
        "OC": OC_ID,
        "target": "law",
        "query": law_name,
        "type": "XML"
    }
    try:
        response = requests.get(SEARCH_URL, params=params)
        root = ET.fromstring(response.content)
        # 검색 결과 중 첫 번째 항목이 현재 시행 중인 최신 법령이야
        mst = root.findtext(".//법령일련번호")
        return mst
    except Exception as e:
        print(f"MST 조회 실패 ({law_name}): {e}")
        return None

def fetch_law_body():
    for category, law_names in LAWS_TO_FETCH.items():
        for name in law_names:
            # 1단계: 이름으로 최신 MST 번호를 따온다
            mst = get_latest_mst(name)
            if not mst:
                continue

            # 2단계: 따온 번호로 본문을 가져온다
            params = {"OC": OC_ID, "target": "law", "MST": mst, "type": "XML"}
            try:
                response = requests.get(SERVICE_URL, params=params)
                root = ET.fromstring(response.content)
                
                path = f"laws/{category}"
                os.makedirs(path, exist_ok=True)
                
                with open(f"{path}/{name}.md", "w", encoding="utf-8") as f:
                    f.write(f"# {name}\n\n")
                    for jo in root.findall(".//조문단위"):
                        title = jo.findtext("조문내용", "")
                        f.write(f"## {title}\n")
                        for hang in jo.findall(".//항내용"):
                            if hang.text: f.write(f"{hang.text}\n")
                        f.write("\n")
                print(f"성공: {name} (최신 MST: {mst})")
            except Exception as e:
                print(f"본문 수집 실패 ({name}): {e}")

if __name__ == "__main__":
    fetch_law_body()
