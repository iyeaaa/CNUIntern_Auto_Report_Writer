import requests
import json
from datetime import datetime, timedelta
import os
import sys
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

# 인턴십 시작일
INTERN_START_DATE = datetime(2025, 9, 1)

def get_target_date():
    """대상 날짜 결정 (인자 또는 현재 날짜)"""
    if len(sys.argv) > 1:
        try:
            return datetime.strptime(sys.argv[1], '%Y-%m-%d')
        except ValueError:
            print("올바른 날짜 형식을 입력해주세요 (YYYY-MM-DD)")
            sys.exit(1)
    return datetime.now()

def calculate_week_number(target_date):
    """인턴십 시작일 기준 주차 계산"""
    days_diff = (target_date - INTERN_START_DATE).days
    week_num = days_diff // 7 + 1
    return f"{week_num}주차"

def get_week_date_range(target_date):
    """해당 주의 시작일부터 대상날짜까지 범위 계산"""
    # 해당 주의 월요일 찾기 (0=월요일, 6=일요일)
    days_from_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_from_monday)
    
    # 인턴십 시작일보다 이전으로 가지 않도록 제한
    if week_start < INTERN_START_DATE:
        week_start = INTERN_START_DATE
    
    return week_start, target_date

def create_gemini_prompt(commits_data, week_range, week_number):
    """Gemini API용 주간 보고서 프롬프트 생성"""
    start_date = week_range[0].strftime('%Y-%m-%d')
    end_date = week_range[1].strftime('%Y-%m-%d')
    
    prompt = f"""
다음은 {week_number} ({start_date} ~ {end_date}) 기간 동안 인턴으로서 진행한 업무 내역입니다.
이 정보를 바탕으로 자연스러운 인턴 주간 보고서를 작성해주세요.

업무 내역:
{commits_data}

작성 지침:
1. 제목은 "# {week_number}" 형식으로 시작
2. 실제 인턴이 작성한 것처럼 자연스럽고 솔직한 톤으로 작성
3. "~했습니다", "~을 진행했습니다" 등 정중한 존댓말 사용
4. 총 13줄 정도의 자연스러운 문장으로 구성
5. 기술적 용어보다는 일반적인 업무 표현 사용 (예: "개발" → "작업", "구현" → "진행")
6. 프로젝트명은 "담당 업무" 또는 "할당받은 작업" 등으로 자연스럽게 표현
7. 주간 업무를 시간 순서대로 자연스럽게 서술
8. 완료한 작업에 대한 간단한 소감이나 배운 점 포함
9. 주요 성과와 다음 주 계획에 대한 언급
10. 마크다운 형식 절대 사용 금지
11. 주간 보고서답게 한 주간의 전체적인 흐름과 성과를 중심으로 작성
12. 안녕하세요 등 인사 금지

마치 실제 인턴이 한 주간의 업무를 돌아보며 솔직하게 작성한 보고서처럼 써주세요.
"""
    return prompt

def generate_content_with_gemini(target_date):
    """Git 커밋 기반으로 주간 보고서 생성"""
    # 주차 및 날짜 범위 계산
    week_number = calculate_week_number(target_date)
    week_range = get_week_date_range(target_date)
    
    print(f"📊 {week_number} 보고서 생성 중...")
    print(f"📅 분석 기간: {week_range[0].strftime('%Y-%m-%d')} ~ {week_range[1].strftime('%Y-%m-%d')}")
    
    # Git 분석기 초기화
    repositories = [
        "/Users/iyein/Documents/ai-show-agent",
        "/Users/iyein/Documents/cleaning-service", 
        "/Users/iyein/Documents/gmpang-linktree-project"
    ]
    
    analyzer = GitAnalyzer(repositories)
    
    # 주간 커밋 데이터 수집
    print("🔍 커밋 정보 수집중...")
    commits_data = analyzer.analyze_commits_for_date_range(
        week_range[0].strftime('%Y-%m-%d'),
        week_range[1].strftime('%Y-%m-%d'),
        author="iyeaaa"
    )
    
    # 실제 커밋이 있는지 확인
    lines = commits_data.strip().split('\n')
    has_actual_commits = any('•' in line for line in lines)
    
    if not has_actual_commits:
        print(f"❌ {week_number}에 해당하는 커밋을 찾을 수 없습니다.")
        return f"{week_number} 주간보고서", f"{week_number} 업무 수행 내용", week_number
    
    try:
        gemini = GeminiAPI()
        prompt = create_gemini_prompt(commits_data, week_range, week_number)
        
        summary = gemini.call_api(prompt, max_tokens=1500)
        
        if not summary:
            return f"{week_number} 주간보고서", f"{week_number} 업무 수행 내용", week_number
        
        # 제목과 내용 분리
        lines = summary.strip().split('\n')
        subject = ""
        contents = ""
        
        for i, line in enumerate(lines):
            if line.startswith(f"# {week_number}"):
                subject = line.replace("# ", "").strip()
                contents = '\n'.join(lines[i+1:]).strip()
                break
        
        if not subject:
            subject = f"{week_number} 주간보고서"
            contents = summary.strip()
        
        return subject, contents, week_number
        
    except Exception as e:
        print(f"제미나이 API 오류: {e}")
        return f"{week_number} 주간보고서", f"{week_number} 업무 수행 내용", week_number

def main():
    # 대상 날짜 결정
    target_date = get_target_date()
    
    print(f"제미나이 API를 사용하여 {target_date.strftime('%Y-%m-%d')} 기준 주간 보고서를 생성중...")
    subject, contents, week_number = generate_content_with_gemini(target_date)
    
    print(f"생성된 제목: {subject}")
    print(f"생성된 내용: {contents[:100]}...")
    
    # 세션 설정
    s = requests.Session()
    s.headers.update({
        "Origin": BASE,
        "Referer": f"{BASE}/student/report/studentBoardWeekAdd",
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
        "bName": "Week",
        "subject": subject,
        "contents": contents,
        "cntn": contents,
        "week": week_number,
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
            print("✓ 주간 보고서가 성공적으로 등록되었습니다!")
            print(f"Insert Result: {insert_result}")
        else:
            print("✗ 주간 보고서 등록에 실패했습니다.")
            print(f"Response: {response_data}")
    except json.JSONDecodeError:
        print("✗ JSON 응답 파싱 실패")
        print(f"Raw response: {r.text[:500]}")

if __name__ == "__main__":
    main()