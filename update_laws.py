import os
import requests
import xml.etree.ElementTree as ET
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. 환경 변수 설정
OC_ID = os.environ.get("LAW_API_KEY")
GDRIVE_JSON_RAW = os.environ.get("GDRIVE_JSON_RAW")

# 2. 메리아스가 알려준 폴더 ID 반영 완료!
FOLDER_IDS = {
    "기본법": "14VatNFyBchzNVtE-EeiGveHoTau5vfTY",
    "회계규칙": "15_hkN9rVU1BdFJuGlrnj6HFh9zgqer-C"
}

SEARCH_URL = "http://www.law.go.kr/DRF/lawSearch.do"
SERVICE_URL = "http://www.law.go.kr/DRF/lawService.do"

# 수집할 법령 목록
LAWS_TO_FETCH = {
    "기본법": ["사립학교법", "사립학교법 시행령", "사립학교법 시행규칙"],
    "회계규칙": ["사학기관 재무·회계 규칙", "사학기관 재무·회계 규칙에 대한 특례규칙", "학교기업 회계처리규칙"]
}

def get_gdrive_service():
    if not GDRIVE_JSON_RAW:
        raise ValueError("GDRIVE_JSON_RAW 환경 변수가 설정되지 않았습니다.")
    creds_dict = json.loads(GDRIVE_JSON_RAW)
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    return build('drive', 'v3', credentials=creds)

def upload_to_gdrive(service, file_path, file_name, folder_id):
    """파일 업로드 및 업데이트 (용량 에러 방지를 위해 supportsAllDrives 적용)"""
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(
        q=query, 
        fields="files(id)", 
        supportsAllDrives=True, 
        includeItemsFromAllDrives=True
    ).execute()
    files = results.get('files', [])
    
    media = MediaFileUpload(file_path, mimetype='text/markdown', resumable=True)

    if files:
        file_id = files[0]['id']
        service.files().update(
            fileId=file_id, 
            media_body=media, 
            supportsAllDrives=True
        ).execute()
        print(f"✅ 업데이트 완료: {file_name}")
    else:
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        service.files().create(
            body=file_metadata, 
            media_body=media, 
            supportsAllDrives=True
        ).execute()
        print(f"🆕 새 파일 생성: {file_name}")

def fetch_law_body():
    service = get_gdrive_service()
    
    for category, law_names in LAWS_TO_FETCH.items():
        category_folder_id = FOLDER_IDS.get(category)
        if not category_folder_id:
            print(f"❌ 폴더 ID 설정 누락: {category}")
            continue
            
        print(f"\n--- {category} 작업 시작 ---")
        for name in law_names:
            params = {"OC": OC_ID, "target": "law", "query": name, "type": "XML"}
            try:
                # 1단계: MST 조회
                search_res = requests.get(SEARCH_URL, params=params)
                root_search = ET.fromstring(search_res.content)
                mst = root_search.findtext(".//법령일련번호")
                
                if not mst:
                    print(f"⚠️ MST 못 찾음 (이름 확인 필요): {name}")
                    continue

                # 2단계: 본문 수집
                params_body = {"OC": OC_ID, "target": "law", "MST": mst, "type": "XML"}
                response = requests.get(SERVICE_URL, params=params_body)
                root = ET.fromstring(response.content)

                # 3단계: 로컬 저장
                folder_path = f"laws/{category}"
                os.makedirs(folder_path, exist_ok=True)
                file_full_path = os.path.join(folder_path, f"{name}.md")
                
                with open(file_full_path, "w", encoding="utf-8") as f:
                    f.write(f"# {name}\n\n")
                    for jo in root.findall(".//조문단위"):
                        title = jo.findtext("조문내용", "")
                        f.write(f"## {title}\n")
                        for hang in jo.findall(".//항내용"):
                            if hang.text: f.write(f"{hang.text}\n")
                        f.write("\n")
                
                # 4단계: 드라이브 업로드
                upload_to_gdrive(service, file_full_path, f"{name}.md", category_folder_id)
                
            except Exception as e:
                print(f"❗ 작업 실패 ({name}): {e}")

if __name__ == "__main__":
    fetch_law_body()
