import os
import requests
import xml.etree.ElementTree as ET
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 환경 변수 및 설정
OC_ID = os.environ.get("LAW_API_KEY")
GDRIVE_JSON_RAW = os.environ.get("GDRIVE_JSON_RAW")
# 메인 폴더 ID (Laws-Folder의 ID)
PARENT_FOLDER_ID = "16zT278nodzMpY-XIM3cn-fBAIrfR8I3Q"

SEARCH_URL = "http://www.law.go.kr/DRF/lawSearch.do"
SERVICE_URL = "http://www.law.go.kr/DRF/lawService.do"

LAWS_TO_FETCH = {
    "기본법": ["사립학교법", "사립학교법 시행령", "사립학교법 시행규칙"],
    "회계규칙": ["사학기관 재무·회계 규칙", "사학기관 재무·회계 규칙에 대한 특례규칙", "학교기업 회계처리규칙"]
}

def get_gdrive_service():
    creds_dict = json.loads(GDRIVE_JSON_RAW)
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name, parent_id):
    """구글 드라이브 내에서 폴더를 찾거나 없으면 생성"""
    query = f"name = '{folder_name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])
    
    if files:
        return files[0]['id']
    else:
        file_metadata = {
            'name': folder_name,
            'parents': [parent_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def upload_to_gdrive(service, file_path, file_name, folder_id):
    """특정 폴더 내에 파일을 업로드하거나 업데이트"""
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])

    media = MediaFileUpload(file_path, mimetype='text/markdown', resumable=True)

    if files:
        file_id = files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"업데이트 완료: {file_name}")
    else:
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        service.files().create(body=file_metadata, media_body=media).execute()
        print(f"새 파일 생성 완료: {file_name}")

def fetch_law_body():
    service = get_gdrive_service()
    
    for category, law_names in LAWS_TO_FETCH.items():
        # 1. 카테고리별 하위 폴더(기본법/회계규칙) ID 확보
        category_folder_id = get_or_create_folder(service, category, PARENT_FOLDER_ID)
        
        for name in law_names:
            # MST 조회 및 법령 본문 수집 로직 (기존과 동일)
            params = {"OC": OC_ID, "target": "law", "query": name, "type": "XML"}
            try:
                search_res = requests.get(SEARCH_URL, params=params)
                mst = ET.fromstring(search_res.content).findtext(".//법령일련번호")
                if not mst: continue

                params_body = {"OC": OC_ID, "target": "law", "MST": mst, "type": "XML"}
                response = requests.get(SERVICE_URL, params=params_body)
                root = ET.fromstring(response.content)
                
                # 로컬 저장
                path = f"laws/{category}"
                os.makedirs(path, exist_ok=True)
                file_full_path = f"{path}/{name}.md"
                
                with open(file_full_path, "w", encoding="utf-8") as f:
                    f.write(f"# {name}\n\n")
                    for jo in root.findall(".//조문단위"):
                        title = jo.findtext("조문내용", "")
                        f.write(f"## {title}\n")
                        for hang in jo.findall(".//항내용"):
                            if hang.text: f.write(f"{hang.text}\n")
                        f.write("\n")
                
                # 2. 구글 드라이브 하위 폴더에 파일 업로드
                upload_to_gdrive(service, file_full_path, f"{name}.md", category_folder_id)
                
            except Exception as e:
                print(f"작업 실패 ({name}): {e}")

if __name__ == "__main__":
    fetch_law_body()
