def fetch_law_body():
    for category, law_names in LAWS_TO_FETCH.items():
        path = f"laws/{category}"
        os.makedirs(path, exist_ok=True)
        
        for name in law_names:
            print(f"[{category}] {name} 본문 및 모든 별표 수집 중...")
            params = {"OC": OC_ID, "target": "law", "query": name, "type": "XML"}
            try:
                # 1. MST 조회
                search_res = requests.get(SEARCH_URL, params=params)
                mst = ET.fromstring(search_res.content).findtext(".//법령일련번호")
                if not mst: continue

                # 2. 본문 수집
                params_body = {"OC": OC_ID, "target": "law", "MST": mst, "type": "XML"}
                response = requests.get(SERVICE_URL, params=params_body)
                root = ET.fromstring(response.content)

                # 3. 파일 저장
                file_name = name.replace("·", "_").replace(" ", "_")
                with open(f"{path}/{file_name}.md", "w", encoding="utf-8") as f:
                    f.write(f"# {name}\n\n")
                    
                    # --- [1] 조문 본문 ---
                    f.write("## 📜 조문 본문\n")
                    for jo in root.findall(".//조문단위"):
                        title = jo.findtext("조문내용", "")
                        f.write(f"### {title}\n")
                        for hang in jo.findall(".//항내용"):
                            if hang.text: f.write(f"{hang.text}\n")
                        f.write("\n")
                    
                    # --- [2] 별표 및 서식 (상세 수집) ---
                    f.write("\n---\n## 📎 별표 및 서식 목록\n")
                    bylpyo_list = root.findall(".//별표단위")
                    
                    if bylpyo_list:
                        for bp in bylpyo_list:
                            bp_title = bp.findtext("별표제목", "제목 없음")
                            bp_link = bp.findtext("별표hwp조회광장연결", "")
                            bp_content = bp.findtext("별표내용", "") # 별표의 텍스트 내용
                            
                            f.write(f"### 📄 {bp_title}\n")
                            if bp_link:
                                f.write(f"- **다운로드/보기**: [국가법령정보센터 링크]({bp_link})\n")
                            
                            if bp_content:
                                f.write(f"#### 텍스트 내용 요약:\n> {bp_content[:500]}... (이하 생략)\n")
                            f.write("\n")
                    else:
                        f.write("해당 법령에는 별표 또는 서식이 없습니다.\n")

                print(f"✅ 수집 완료: {path}/{file_name}.md")
            except Exception as e:
                print(f"❗ 오류 발생 ({name}): {e}")
