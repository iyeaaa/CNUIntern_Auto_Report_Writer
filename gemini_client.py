"""
Google Gemini API 통신 모듈
기존 코드를 바탕으로 간소화된 버전
"""

import os
import json
import requests
from typing import Optional
import time

class GeminiAPI:
    """Google Gemini API 클래스"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Google Gemini API 키 (없으면 환경변수에서 읽음)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            print("⚠️ GEMINI_API_KEY가 설정되지 않았습니다.")
            print("💡 다음 방법 중 하나를 사용하세요:")
            print("   1. 환경변수: export GEMINI_API_KEY='your_api_key'")
            print("   2. Google AI Studio에서 API 키 발급")
            raise ValueError("GEMINI_API_KEY가 필요합니다.")

        # API 키 유효성 기본 검증
        if not self.api_key.startswith('AIza'):
            print("⚠️ API 키 형식이 올바르지 않습니다.")
            print("💡 Google AI Studio에서 발급받은 API 키를 사용하세요.")

        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.5-flash-lite"

    def call_api(self, prompt: str, max_tokens: int = 1000, max_retries: int = 3) -> Optional[str]:
        """
        Gemini API 호출 (재시도 기능 포함)

        Args:
            prompt: API에 전송할 프롬프트
            max_tokens: 최대 토큰 수
            max_retries: 최대 재시도 횟수

        Returns:
            API 응답 텍스트 (실패시 None)
        """
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

                headers = {
                    'Content-Type': 'application/json'
                }

                data = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": max_tokens,
                    }
                }

                response = requests.post(url, headers=headers, data=json.dumps(data))
                response.raise_for_status()

                result = response.json()

                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        return candidate['content']['parts'][0]['text']

                print("❌ Gemini API 응답에서 콘텐츠를 찾을 수 없습니다.")
                return None

            # 재시도 로직
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 점진적 대기 시간
                    print(f"⚠️ 시도 {attempt + 1}/{max_retries} 실패, {wait_time}초 후 재시도...")
                    print(f"   오류: {str(e)}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ 최대 재시도 횟수 ({max_retries})를 초과했습니다.")
                    print(f"   마지막 오류: {str(e)}")
                    return None
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"⚠️ 시도 {attempt + 1}/{max_retries} 실패, {wait_time}초 후 재시도...")
                    print(f"   오류: {str(e)}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ 최대 재시도 횟수 ({max_retries})를 초과했습니다.")
                    print(f"   마지막 오류: {str(e)}")
                    return None

def test_gemini_api(api_key: str = None):
    """Gemini API 테스트 함수"""
    try:
        print("🔍 Gemini API 연결 테스트 중...")
        api = GeminiAPI(api_key)
        result = api.call_api("안녕하세요. 간단한 인사말을 작성해주세요.", max_retries=2)
        if result:
            print("✅ Gemini API 테스트 성공!")
            print(f"📝 응답: {result[:100]}...")
            return True
        else:
            print("❌ Gemini API 테스트 실패!")
            return False
    except Exception as e:
        print(f"❌ Gemini API 테스트 중 오류: {str(e)}")
        return False

if __name__ == "__main__":
    test_gemini_api()