#!/usr/bin/env python3
"""
GitHub 일일 커밋 분석 프로그램
사용자가 입력한 날짜의 커밋 내역을 분석하여 Gemini API로 요약을 생성합니다.
"""

import sys
import os
from datetime import datetime
from git_analyzer import GitAnalyzer
from gemini_client import GeminiAPI

def validate_date(date_string):
    """날짜 형식 검증 (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_user_input():
    """사용자로부터 날짜 입력받기"""
    while True:
        date_input = input("분석할 날짜를 입력하세요 (YYYY-MM-DD): ").strip()
        
        if validate_date(date_input):
            return date_input
        else:
            print("❌ 올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식으로 입력해주세요.")
            print("예시: 2025-09-10")

def create_gemini_prompt(commits_data, date):
    """Gemini API용 프롬프트 생성"""
    prompt = f"""
다음은 {date} 날짜에 iyeaaa 계정으로 진행한 Git 커밋 내역입니다.
이 정보를 바탕으로 하루 개발 활동을 요약해주세요.

커밋 정보:
{commits_data}

요구사항:
1. 제목은 "# {date}" 형식으로 시작
2. 존댓말("~했습니다") 체로 작성
3. 총 7줄 정도의 자연스러운 서술식 문장
4. 각 프로젝트별 주요 작업 내용과 전체적인 개발 성과를 포함
5. 기술적 성취나 문제 해결에 대한 내용도 언급
6. 마크다운 형식을 절대 사용하지 말것

자연스럽고 읽기 쉬운 보고서 형식으로 작성해주세요.
"""
    return prompt

def main():
    """메인 실행 함수"""
    print("🔍 GitHub 일일 커밋 분석기")
    print("=" * 40)
    
    # 사용자 입력 받기
    target_date = get_user_input()
    print(f"\n📅 {target_date} 날짜의 커밋을 분석중...")
    
    # Git 분석기 초기화
    repositories = [
        "/Users/iyein/Documents/ai-show-agent",
        "/Users/iyein/Documents/cleaning-service", 
        "/Users/iyein/Documents/gmpang-linktree-project"
    ]
    
    analyzer = GitAnalyzer(repositories)
    
    # 커밋 데이터 수집
    print("🔍 커밋 정보 수집중...")
    commits_data = analyzer.analyze_commits_for_date(target_date, author="iyeaaa")
    
    # 실제 커밋이 있는지 확인 (모든 저장소에서 "해당 날짜에 커밋이 없습니다"인지 체크)
    lines = commits_data.strip().split('\n')
    has_actual_commits = any('•' in line for line in lines)
    
    if not has_actual_commits:
        print(f"❌ {target_date}에 해당하는 커밋을 찾을 수 없습니다.")
        print("다른 날짜를 시도해보세요.")
        return
    
    print("📝 커밋 정보:")
    print(commits_data)
    print("\n" + "=" * 40)
    
    # Gemini API로 요약 생성
    print("🤖 Gemini AI로 보고서 생성중...")
    try:
        gemini = GeminiAPI()
        prompt = create_gemini_prompt(commits_data, target_date)
        
        summary = gemini.call_api(prompt, max_tokens=1000)
        
        if summary:
            print("\n📋 생성된 보고서:")
            print("=" * 40)
            print(summary)
        else:
            print("❌ 보고서 생성에 실패했습니다.")
            
    except Exception as e:
        print(f"❌ Gemini API 오류: {str(e)}")
        print("GEMINI_API_KEY 환경변수가 설정되어 있는지 확인해주세요.")

if __name__ == "__main__":
    main()