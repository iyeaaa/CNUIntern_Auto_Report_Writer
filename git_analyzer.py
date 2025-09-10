"""
Git 저장소 분석 모듈
여러 저장소에서 특정 날짜의 커밋 정보를 추출합니다.
"""

import os
import subprocess
from datetime import datetime

class GitAnalyzer:
    """Git 저장소 분석 클래스"""
    
    def __init__(self, repositories):
        """
        Args:
            repositories: 분석할 저장소 경로 리스트
        """
        self.repositories = repositories
    
    def is_git_repository(self, path):
        """Git 저장소인지 확인"""
        return os.path.exists(os.path.join(path, '.git'))
    
    def get_commits_for_date(self, repo_path, date, author=None):
        """특정 날짜의 커밋 정보 추출"""
        if not self.is_git_repository(repo_path):
            return f"❌ {os.path.basename(repo_path)}: Git 저장소가 아닙니다."
        
        try:
            # Git log 명령어 구성
            cmd = [
                'git', '-C', repo_path, 'log',
                '--since', f'{date} 00:00:00',
                '--until', f'{date} 23:59:59',
                '--pretty=format:%h|%s|%an|%ad|%D',
                '--date=short'
            ]
            
            # 작성자 필터 추가
            if author:
                cmd.extend(['--author', author])
            
            # Git 명령어 실행
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = result.stdout.strip()
            if not commits:
                return f"📁 {os.path.basename(repo_path)}: 해당 날짜에 커밋이 없습니다."
            
            # 커밋 정보 포맷팅
            repo_name = os.path.basename(repo_path)
            formatted_commits = f"\n📁 {repo_name}:\n"
            
            for line in commits.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 4:
                        hash_short = parts[0]
                        message = parts[1]
                        author_name = parts[2]
                        date_str = parts[3]
                        formatted_commits += f"  • {hash_short}: {message} (by {author_name})\n"
            
            # 변경된 파일 통계 추가
            stats_cmd = [
                'git', '-C', repo_path, 'log',
                '--since', f'{date} 00:00:00',
                '--until', f'{date} 23:59:59',
                '--stat', '--oneline'
            ]
            
            if author:
                stats_cmd.extend(['--author', author])
            
            stats_result = subprocess.run(
                stats_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if stats_result.stdout.strip():
                # 변경된 파일 수 계산
                lines = stats_result.stdout.strip().split('\n')
                file_changes = []
                for line in lines:
                    if '|' in line and ('+' in line or '-' in line):
                        filename = line.split('|')[0].strip()
                        if filename and not filename.startswith(' '):
                            file_changes.append(filename)
                
                if file_changes:
                    formatted_commits += f"    변경된 파일 ({len(file_changes)}개): {', '.join(file_changes[:5])}"
                    if len(file_changes) > 5:
                        formatted_commits += f" 외 {len(file_changes) - 5}개"
                    formatted_commits += "\n"
            
            return formatted_commits
            
        except subprocess.CalledProcessError as e:
            return f"❌ {os.path.basename(repo_path)}: Git 명령어 실행 실패 - {str(e)}"
        except Exception as e:
            return f"❌ {os.path.basename(repo_path)}: 오류 발생 - {str(e)}"
    
    def get_commits_for_date_range(self, repo_path, start_date, end_date, author=None):
        """특정 날짜 범위의 커밋 정보 추출"""
        if not self.is_git_repository(repo_path):
            return f"❌ {os.path.basename(repo_path)}: Git 저장소가 아닙니다."
        
        try:
            # Git log 명령어 구성
            cmd = [
                'git', '-C', repo_path, 'log',
                '--since', f'{start_date} 00:00:00',
                '--until', f'{end_date} 23:59:59',
                '--pretty=format:%h|%s|%an|%ad|%D',
                '--date=short'
            ]
            
            # 작성자 필터 추가
            if author:
                cmd.extend(['--author', author])
            
            # Git 명령어 실행
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = result.stdout.strip()
            if not commits:
                return f"📁 {os.path.basename(repo_path)}: 해당 기간에 커밋이 없습니다."
            
            # 커밋 정보 포맷팅
            repo_name = os.path.basename(repo_path)
            formatted_commits = f"\n📁 {repo_name}:\n"
            
            for line in commits.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 4:
                        hash_short = parts[0]
                        message = parts[1]
                        author_name = parts[2]
                        date_str = parts[3]
                        formatted_commits += f"  • {hash_short}: {message} (by {author_name}, {date_str})\n"
            
            # 변경된 파일 통계 추가
            stats_cmd = [
                'git', '-C', repo_path, 'log',
                '--since', f'{start_date} 00:00:00',
                '--until', f'{end_date} 23:59:59',
                '--stat', '--oneline'
            ]
            
            if author:
                stats_cmd.extend(['--author', author])
            
            stats_result = subprocess.run(
                stats_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if stats_result.stdout.strip():
                # 변경된 파일 수 계산
                lines = stats_result.stdout.strip().split('\n')
                file_changes = []
                for line in lines:
                    if '|' in line and ('+' in line or '-' in line):
                        filename = line.split('|')[0].strip()
                        if filename and not filename.startswith(' '):
                            file_changes.append(filename)
                
                if file_changes:
                    formatted_commits += f"    변경된 파일 ({len(file_changes)}개): {', '.join(file_changes[:5])}"
                    if len(file_changes) > 5:
                        formatted_commits += f" 외 {len(file_changes) - 5}개"
                    formatted_commits += "\n"
            
            return formatted_commits
            
        except subprocess.CalledProcessError as e:
            return f"❌ {os.path.basename(repo_path)}: Git 명령어 실행 실패 - {str(e)}"
        except Exception as e:
            return f"❌ {os.path.basename(repo_path)}: 오류 발생 - {str(e)}"

    def analyze_commits_for_date(self, date, author=None):
        """모든 저장소의 특정 날짜 커밋 분석"""
        all_commits = []
        
        print(f"📊 분석 대상 저장소: {len(self.repositories)}개")
        
        for repo_path in self.repositories:
            if not os.path.exists(repo_path):
                all_commits.append(f"❌ {os.path.basename(repo_path)}: 경로가 존재하지 않습니다.")
                continue
            
            commits = self.get_commits_for_date(repo_path, date, author)
            all_commits.append(commits)
        
        return "\n".join(all_commits)
    
    def analyze_commits_for_date_range(self, start_date, end_date, author=None):
        """모든 저장소의 특정 날짜 범위 커밋 분석"""
        all_commits = []
        
        print(f"📊 분석 대상 저장소: {len(self.repositories)}개")
        print(f"📅 분석 기간: {start_date} ~ {end_date}")
        
        for repo_path in self.repositories:
            if not os.path.exists(repo_path):
                all_commits.append(f"❌ {os.path.basename(repo_path)}: 경로가 존재하지 않습니다.")
                continue
            
            commits = self.get_commits_for_date_range(repo_path, start_date, end_date, author)
            all_commits.append(commits)
        
        return "\n".join(all_commits)
    
    def get_repository_status(self):
        """저장소 상태 확인"""
        status_info = []
        
        for repo_path in self.repositories:
            repo_name = os.path.basename(repo_path)
            
            if not os.path.exists(repo_path):
                status_info.append(f"❌ {repo_name}: 경로 없음")
                continue
            
            if not self.is_git_repository(repo_path):
                status_info.append(f"❌ {repo_name}: Git 저장소 아님")
                continue
            
            status_info.append(f"✅ {repo_name}: 정상")
        
        return status_info