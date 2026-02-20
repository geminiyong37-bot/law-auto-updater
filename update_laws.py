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
PARENT_FOLDER_ID = "16zT278nodzMpY-XIM3cn-fBAIrfR8I3Q"

SEARCH_URL = "http://www.law.go.kr/DRF/lawSearch.do"
SERVICE_URL = "http://www.law.go.kr/DRF/lawService.do"

LAWS_TO_FETCH = {
    "기본법": ["사립학교법", "사립학교법 시행령", "사립학교법 시행규칙"],
    "회계규칙": ["사학기관 재무·회계 규칙", "사학기관 재무·회계 규칙에 대한 특례규칙", "학교기업 회계처리규칙"]
}

def get_gdrive_service():
    if not GDRIVE_JSON_RAW:
        raise ValueError("GDRIVE_JSON_RAW 환경 변수가 없습니다.")
    creds_dict = json.loads(GDRIVE_JSON_RAW)
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name, parent_id):
    query = f"name = '{folder_name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    else:
        file_metadata = {'name': folder_name, 'parents': [parent_id], 'mimeType': 'application/vnd.google-apps.folder'}
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def upload_to_gdrive(service, file_path, file_name, folder_id):
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])
    media = MediaFileUpload(file_path, mimetype='text/markdown', resumable=True)

    if files:
        file_id = files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"구글 드라이브 업데이트 완료: {file_name}")
    else:
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        service.files().create(body=file_metadata, media_body=media).execute()
        print(f"구글 드라이브 새 파일 생성: {file_name}")

def fetch_law_body():
    service = get_gdrive_service()
    for category, law_names in LAWS_TO_FETCH.items():
        category_folder_id = get_or_create_folder(service, category, PARENT_FOLDER_ID)
        for name in law_names:
            params = {"OC": OC_ID, "target": "law", "query": name, "type": "XML"}
            try:
                # 1. MST 조회
                search_res = requests.get(SEARCH_URL, params=params)
                root_search = ET.fromstring(search_res.content)
                mst = root_search.findtext(".//법령일련번호")
                if not mst:
                    print(f"MST 못 찾음: {name}")
                    continue

                # 2. 본문 수집
                params_body = {"OC": OC_ID, "target": "law", "MST": mst, "type": "XML"}
                response = requests.get(SERVICE_URL, params=params_body)
                root = ET.fromstring(response.content)

                # 3. 로컬 파일 저장
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
                
                # 4. 드라이브 업로드 (파일 닫힌 후 실행)
                upload_to_gdrive(service, file_full_path, f"{name}.md", category_folder_id)
            except Exception as e:
                print(f"작업 실패 ({name}): {e}")

# 바로 이 부분이 "시작 버튼"이야! 이 아래까지 다 복사해야 해.
if __name__ == "__main__":
    fetch_law_body()
