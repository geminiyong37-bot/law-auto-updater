function syncLawsFromGithub() {
  const GITHUB_USER = "geminiyong37-bot";
  const REPO_NAME = "law-auto-updater";
  const ROOT_FOLDER_ID = "16zT278nodzMpY-XIM3cn-fBAIrfR8I3Q"; // Laws-Folder ID
  
  // 1. 분류 정의: 깃허브의 원본 폴더별로 구글 드라이브의 어느 타겟 폴더로 갈지 지정
  const githubStructure = {
    "사립대학": {
      targets: ["사립대학"],
      files: [
        "사립학교법.md", "사립학교법_시행령.md", "사학기관_재무_회계_규칙.md", 
        "사학기관_재무_회계_규칙에_대한_특례규칙.md", "대학설립_운영_규정.md", 
        "대학설립_운영_규정_시행규칙.md", "사이버대학_설립_운영_규정.md", "대학_등록금에_관한_규칙.md",
        "사학기관_외부회계감사_유의사항.md", "사학기관_외부회계감사_감리에_관한_고시.md", 
        "사학기관_외부감사인_지정_등에_관한_고시.md"
      ]
    },
    "평생교육": {
      targets: ["사립대학"],
      files: ["평생교육법.md", "평생교육법_시행령.md", "평생교육법_시행규칙.md"]
    },
    "부속병원": {
      targets: ["사립대학"],
      files: ["의료기관_회계기준_규칙.md", "재무제표_세부_작성방법.md"]
    },
    "산학협력단": {
      targets: ["산학협력단"],
      files: [
        "산업교육진흥_및_산학연협력촉진에_관한_법률.md", "산업교육진흥_및_산학연협력촉진에_관한_법률_시행령.md", 
        "산업교육진흥_및_산학연협력촉진에_관한_법률_시행규칙.md", "국가연구개발혁신법.md", 
        "국가연구개발혁신법_시행령.md", "국가연구개발혁신법_시행규칙.md",
        "산학협력단회계처리규칙.md", "국가연구개발사업_연구개발비_사용_기준.md", 
        "산학연협력기술지주회사_설립절차_등에_관한_규정.md", "계약학과_설치_운영_규정.md", 
        "국가연구개발_시설_장비의_관리_등에_관한_표준지침.md"
      ]
    },
    "재외교육기관": {
      targets: ["재외교육기관"],
      files: [
        "재외국민의_교육지원_등에_관한_법률.md", "재외국민의_교육지원_등에_관한_법률_시행령.md", 
        "재외국민의_교육지원_등에_관한_법률_시행규칙.md", "재외공관_비소모품_관리규정.md"
      ]
    },
    "학교기업": {
      targets: ["사립대학", "산학협력단"],
      files: ["학교기업_회계처리규칙.md"]
    },
    "기본재산": {
      targets: ["사립대학"],
      files: ["교육용_기본재산_처분에_대한_기준_고시.md"]
    },
    "세무": {
      targets: ["사립대학", "산학협력단"],
      files: [
        "법인세법.md", "법인세법_시행령.md", "법인세법_시행규칙.md",
        "상속세_및_증여세법.md", "상속세_및_증여세법_시행령.md", "상속세_및_증여세법_시행규칙.md",
        "부가가치세법.md", "부가가치세법_시행령.md", "부가가치세법_시행규칙.md",
        "소득세법.md", "소득세법_시행령.md", "소득세법_시행규칙.md",
        "사립학교교직원_연금법.md", "사립학교교직원_연금법_시행령.md",
        "근로자퇴직급여_보장법.md", "근로자퇴직급여_보장법_시행령.md",
        "공익법인의_설립_운영에_관한_법률.md", "공익법인의_설립_운영에_관한_법률_시행령.md",
        "지방세법.md", "지방세법_시행령.md", "지방세법_시행규칙.md"
      ]
    }
  };
  
  const rootFolder = DriveApp.getFolderById(ROOT_FOLDER_ID);
  
  // 2. 최종 3개 폴더(사립대학, 산학협력단, 재외교육기관)만 준비
  const targetFolderNames = ["사립대학", "산학협력단", "재외교육기관"];
  const targetFolders = {};
  
  targetFolderNames.forEach(name => {
    const folders = rootFolder.getFoldersByName(name);
    targetFolders[name] = folders.hasNext() ? folders.next() : rootFolder.createFolder(name);
  });
  
  // 3. 깃허브에서 .md 파일만 가져와서 동기화
  for (let sourceFolder in githubStructure) {
    const config = githubStructure[sourceFolder];
    
    config.files.forEach(fileName => {
      // 오직 .md 확장자 파일만 깃허브 raw 경로에서 호출
      const url = `https://raw.githubusercontent.com/${GITHUB_USER}/${REPO_NAME}/main/laws/${sourceFolder}/${fileName}`;
      
      try {
        const response = UrlFetchApp.fetch(url);
        const content = response.getContentText();
        
        // 지정된 타겟 폴더들에 파일 저장
        config.targets.forEach(targetName => {
          const folder = targetFolders[targetName];
          const existingFiles = folder.getFilesByName(fileName);
          
          if (existingFiles.hasNext()) {
            existingFiles.next().setContent(content);
            console.log(`✅ [업데이트] ${targetName}/${fileName}`);
          } else {
            folder.createFile(fileName, content);
            console.log(`🆕 [신규생성] ${targetName}/${fileName}`);
          }
        });
        
      } catch (e) {
        console.log(`❌ 실패: ${sourceFolder}/${fileName} - ${e.message}`);
      }
    });
  }
}
