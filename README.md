⚖️ 국가법령 자동 수집 및 동기화 시스템 (Auto-Sync)
법제처 API를 사용하여 특정 법령 데이터를 수집하고, GitHub Actions와 Google Apps Script를 통해 구글 드라이브까지 자동으로 업데이트하는 무인 자동화 프로젝트입니다.

🔄 워크플로우 아키텍처
GitHub Actions: 매일 한국 시간 새벽 4시에 파이썬 스크립트를 자동 실행합니다.

Python Script: 법제처 API로 법령 본문 및 별표 데이터를 가져와 /laws 폴더에 업데이트합니다.

Git Commit & Push: 변경된 데이터가 있다면 저장소에 자동으로 커밋하여 이력을 남깁니다.

Google Apps Script (GAS): 깃허브 저장소의 최신 데이터를 읽어와 구글 드라이브 파일(.md, .txt)을 동기화합니다.

📂 프로젝트 구성
1. Python 수집기 (update_laws.py)
법제처 오픈 API 기반 조문/항/별표 텍스트 추출.

환경 변수 LAW_API_KEY를 통해 보안 인증 수행.

2. GitHub Actions (.github/workflows/daily_update.yml)
스케줄링: cron: '0 19 * * *' (UTC 기준 19시 = KST 기준 04시).

비밀 키 관리: GitHub Secrets를 통해 API 키를 안전하게 주입.

자동 커밋: 업데이트된 법령 데이터가 있을 경우 AutoUpdater 이름으로 자동 푸시.

3. 구글 앱스 스크립트 (sync.gs)
구글 드라이브 내 지정된 폴더 구조 유지 및 파일 동기화.

.md 및 .txt 동시 생성으로 범용성 확보.

🛠️ 설정 및 사용 방법
1. GitHub Secrets 설정
GitHub 저장소의 Settings > Secrets and variables > Actions 메뉴에서 다음 항목을 등록해야 합니다.

LAW_API_KEY: 법제처에서 발급받은 오픈 API 인증키

2. 구글 앱스 스크립트 설정
GAS 코드 내 GITHUB_USER, REPO_NAME, ROOT_FOLDER_ID를 본인의 환경에 맞게 수정합니다.

GAS 트리거를 설정(예: 매일 오전 5시)하면 깃허브 업데이트 직후 드라이브 동기화가 이루어집니다.

3. 수동 실행
GitHub 저장소의 Actions 탭에서 Daily Law Update 워크플로우를 선택한 뒤 Run workflow를 클릭하여 즉시 실행할 수 있습니다.

⚠️ 주의사항
파일 일치: 파이썬 스크립트에서 생성하는 파일명(공백 제거 등)과 GAS의 folderMap에 정의된 파일명이 정확히 일치해야 합니다.

권한: GitHub Actions가 저장소에 푸시할 수 있도록 Settings > Actions > General에서 Workflow permissions를 Read and write permissions로 설정해야 합니다.
