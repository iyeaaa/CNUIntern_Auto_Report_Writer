import requests
import json
from datetime import datetime
import os
from gemini_client import GeminiAPI
from git_analyzer import GitAnalyzer

# 환경변수에서 설정값 로드
BASE = os.getenv('BASE_URL', 'https://cnujob.cnu.ac.kr')
COOKIE = os.getenv('SESSION_COOKIE')

# 필수 환경변수 체크
if not COOKIE:
    print("⚠️ SESSION_COOKIE 환경변수가 설정되지 않았습니다.")
    print("💡 export SESSION_COOKIE='your_cookie_string'")
    raise ValueError("SESSION_COOKIE가 필요합니다.")

def create_gemini_prompt(commits_data, date):
    """Gemini API용 프롬프트 생성"""
    prompt = f"""
다음은 {date} 날짜에 인턴으로서 진행한 업무 내역입니다.
이 정보를 바탕으로 자연스러운 인턴 일일 보고서를 작성해주세요.

업무 내역:
{commits_data}

작성 지침:
1. 제목은 "# {date}" 형식으로 시작
2. 실제 인턴이 작성한 것처럼 자연스럽고 솔직한 톤으로 작성
3. "~했습니다", "~을 진행했습니다" 등 정중한 존댓말 사용
4. 총 10줄 정도의 자연스러운 문장으로 구성
5. 기술적 용어보다는 일반적인 업무 표현 사용 (예: "개발" → "작업", "구현" → "진행")
6. 프로젝트명은 "담당 업무" 또는 "할당받은 작업" 등으로 자연스럽게 표현
7. 하루 업무를 시간 순서대로 자연스럽게 서술
8. 완료한 작업에 대한 간단한 소감이나 배운 점 포함
9. 마크다운 형식 절대 사용 금지
10. 일기 처럼 작성하지말고, 그냥 오늘 하루 뭐했는지 기록하는 용도처럼 작성
11. 안녕하세요 등 인사 금지

마치 실제 인턴이 하루 업무를 돌아보며 솔직하게 작성한 보고서처럼 써주세요.
"""
    return prompt

def generate_content_with_gemini(date_str):
    """Git 커밋 기반으로 일일 보고서 생성"""
    # Git 분석기 초기화
    repositories = [
        "/Users/iyein/Documents/ai-show-agent",
        "/Users/iyein/Documents/cleaning-service", 
        "/Users/iyein/Documents/gmpang-linktree-project"
    ]
    
    analyzer = GitAnalyzer(repositories)
    
    # 커밋 데이터 수집
    print("🔍 커밋 정보 수집중...")
    commits_data = analyzer.analyze_commits_for_date(date_str, author="iyeaaa")
    
    # 실제 커밋이 있는지 확인
    lines = commits_data.strip().split('\n')
    has_actual_commits = any('•' in line for line in lines)
    
    if not has_actual_commits:
        print(f"❌ {date_str}에 해당하는 커밋을 찾을 수 없습니다.")
        return f"일일 보고서 - {date_str}", f"{date_str} 업무 수행 내용"
    
    try:
        gemini = GeminiAPI()
        prompt = create_gemini_prompt(commits_data, date_str)
        
        summary = gemini.call_api(prompt, max_tokens=1000)
        
        if not summary:
            return f"일일 보고서 - {date_str}", f"{date_str} 업무 수행 내용"
        
        # 제목과 내용 분리
        lines = summary.strip().split('\n')
        subject = ""
        contents = ""
        
        for i, line in enumerate(lines):
            if line.startswith(f"# {date_str}"):
                subject = line.replace("# ", "").strip()
                contents = '\n'.join(lines[i+1:]).strip()
                break
        
        if not subject:
            subject = f"일일 보고서 - {date_str}"
            contents = summary.strip()
        
        return subject, contents
        
    except Exception as e:
        print(f"제미나이 API 오류: {e}")
        return f"일일 보고서 - {date_str}", f"{date_str} 업무 수행 내용"

def main():
    # 사용자로부터 날짜 입력받기
    date_input = input("날짜를 입력하세요 (YYYY-MM-DD 형식, 예: 2025-09-10): ").strip()
    
    # 날짜 형식 검증
    try:
        datetime.strptime(date_input, '%Y-%m-%d')
    except ValueError:
        print("올바른 날짜 형식을 입력해주세요 (YYYY-MM-DD)")
        return
    
    print(f"제미나이 API를 사용하여 {date_input} 날짜의 콘텐츠를 생성중...")
    subject, contents = generate_content_with_gemini(date_input)
    
    print(f"생성된 제목: {subject}")
    print(f"생성된 내용: {contents}...")
    
    # 세션 설정
    s = requests.Session()
    s.headers.update({
        "Origin": BASE,
        "Referer": f"{BASE}/student/report/studentBoardDayAdd",
        "User-Agent": "Mozilla/5.0",
    })
    
    # 쿠키 설정
    for kv in COOKIE.split("; "):
        k, v = kv.split("=", 1)
        s.cookies.set(k, v, domain="cnujob.cnu.ac.kr")

    # 환경변수에서 사용자 정보 로드
    seq_stu = os.getenv('STUDENT_SEQ')
    seq_corp = os.getenv('CORP_SEQ')
    seq_class = os.getenv('CLASS_SEQ')
    seq_lect = os.getenv('LECT_SEQ')
    student_id = os.getenv('STUDENT_ID')
    
    # 필수 환경변수 체크
    required_vars = {
        'STUDENT_SEQ': seq_stu,
        'CORP_SEQ': seq_corp,
        'CLASS_SEQ': seq_class,
        'LECT_SEQ': seq_lect,
        'STUDENT_ID': student_id
    }
    
    missing_vars = [k for k, v in required_vars.items() if not v]
    if missing_vars:
        print(f"⚠️ 다음 환경변수들이 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("💡 .env.example 파일을 참고하여 환경변수를 설정해주세요.")
        raise ValueError("필수 환경변수가 누락되었습니다.")

    # 세션 데이터
    data = {
        "seqStu": seq_stu,
        "seqCorp": seq_corp, 
        "seqClass": seq_class,
        "seqLect": seq_lect,
        "id": student_id,
        "bName": "Day",
        "subject": subject,
        "contents": contents,
        "cntn": contents,
        "day": date_input,
    }

    # 게시물 전송
    r = s.post(f"{BASE}/student/report/studentBoardAddProc", data=data, timeout=20)
    print(f"Status Code: {r.status_code}")
    print(f"URL: {r.url}")

    # 응답 처리
    try:
        response_data = r.json()
        insert_result = response_data.get("insertResult", 0)
        if insert_result > 0:
            print("✓ 게시물이 성공적으로 등록되었습니다!")
            print(f"Insert Result: {insert_result}")
        else:
            print("✗ 게시물 등록에 실패했습니다.")
            print(f"Response: {response_data}")
    except json.JSONDecodeError:
        print("✗ JSON 응답 파싱 실패")
        print(f"Raw response: {r.text[:500]}")

if __name__ == "__main__":
    main()