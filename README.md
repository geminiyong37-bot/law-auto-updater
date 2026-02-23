⚖️ 국가법령 자동 수집 및 동기화 시스템
법제처 API를 사용하여 특정 법령 데이터를 수집하고, 이를 깃허브(GitHub)를 거쳐 구글 드라이브(Google Drive)에 자동으로 동기화하는 프로젝트입니다.

🚀 시스템 구조
Python Script: 법제처 오픈 API를 통해 사립학교법 및 관련 회계 규칙을 수집하여 .md 파일로 저장합니다.

GitHub Repository: 수집된 법령 데이터를 버전 관리하고 저장소에 호스팅합니다.

Google Apps Script (GAS): 깃허브의 Raw 컨텐츠를 불러와 구글 드라이브 내 지정된 폴더에 .md 및 .txt 형식으로 자동 업데이트합니다.

📂 프로젝트 구성
1. Python 수집기 (law_fetcher.py)
국가법령정보센터 오픈 API를 활용하여 법령 본문과 별표/서식 내용을 텍스트 형태로 추출합니다.

주요 기능:

법령일련번호(MST) 자동 조회

조문 본문 및 항 내용 수집

별표 및 서식의 텍스트 데이터 추출

카테고리별 폴더 자동 분류 저장

환경 변수: LAW_API_KEY (법제처 API 키 필요)

2. 구글 앱스 스크립트 (sync.gs)
깃허브 저장소와 구글 드라이브를 연결하는 가교 역할을 합니다.

동기화 대상:

기본법: 사립학교법, 시행령, 시행규칙

회계규칙: 재무·회계 규칙, 특례규칙, 학교기업 회계처리규칙

특징:

기존 파일 존재 시 내용 업데이트 (Overwrite)

신규 파일 생성 시 폴더 자동 생성

.md와 .txt 두 가지 확장자로 동시 저장하여 호환성 확보

🛠️ 사용 방법
Step 1: Python 스크립트 실행
법제처에서 API 키를 발급받습니다.

로컬 환경 변수에 LAW_API_KEY를 설정합니다.

스크립트를 실행하여 laws/ 폴더에 데이터가 생성되는지 확인합니다.

Bash
python law_fetcher.py
Step 2: GitHub 업로드
생성된 laws/ 폴더와 코드를 깃허브 저장소에 푸시합니다.

Step 3: Google Apps Script 설정
구글 드라이브에 법령을 저장할 루트 폴더를 생성하고 Folder ID를 복사합니다.

Google Apps Script에서 새 프로젝트를 생성합니다.

제공된 GAS 코드를 복사하고 다음 변수를 수정합니다.

GITHUB_USER: 본인의 깃허브 ID

REPO_NAME: 저장소 이름

ROOT_FOLDER_ID: 복사한 구글 드라이브 폴더 ID

syncLawsFromGithub 함수를 실행하거나 트리거를 설정하여 자동화합니다.

⚠️ 주의사항
API 호출 제한: 법제처 API 및 구글 서비스 호출 제한 범위를 준수하십시오.

보안: LAW_API_KEY는 절대 Public 저장소에 직접 커밋하지 마십시오. (.gitignore 활용 권장)

경로 일치: Python 스크립트가 생성하는 폴더 구조와 GAS의 folderMap 경로가 일치해야 정상적으로 동기화됩니다.
