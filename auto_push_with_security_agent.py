#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 자동 푸시 스크립트 (보안 에이전트 통합)
보안 에이전트를 사용하여 GitHub Personal Access Token 관리
"""

import subprocess
import sys
import os
from pathlib import Path

# 보안 에이전트 통합
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from scripts.security_agent_manager import get_security_agent, get_secret
    SECURITY_AGENT_AVAILABLE = True
except ImportError:
    SECURITY_AGENT_AVAILABLE = False
    print("⚠️ 보안 에이전트를 불러올 수 없습니다. 수동 인증이 필요할 수 있습니다.")

def find_git():
    """Git 실행 파일 경로 찾기"""
    git_paths = [
        "git",  # PATH에 있는 경우
        r"F:\Git\cmd\git.exe",
        r"F:\Git\bin\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
        r"C:\Program Files\Git\cmd\git.exe",
    ]
    
    for git_path in git_paths:
        try:
            if git_path == "git":
                result = subprocess.run(
                    ["where", "git"],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    return "git"
            elif os.path.exists(git_path):
                return git_path
        except:
            continue
    
    return None

def run_git(git_cmd, args, cwd=None, env=None):
    """Git 명령 실행"""
    try:
        full_cmd = [git_cmd] + args
        
        # 환경 변수 설정
        if env is None:
            env = os.environ.copy()
        
        result = subprocess.run(
            full_cmd,
            cwd=cwd or os.getcwd(),
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False, "", str(e)

def setup_git_credentials(git_cmd, repo_dir, token=None):
    """Git 인증 설정"""
    if not token:
        # 보안 에이전트에서 토큰 가져오기
        if SECURITY_AGENT_AVAILABLE:
            try:
                agent = get_security_agent()
                token = agent.get_env_var("GITHUB_TOKEN") or agent.get_env_var("GITHUB_PAT")
            except:
                pass
    
    if token:
        # URL에 토큰 포함하여 원격 저장소 설정
        remote_url = f"https://{token}@github.com/mkmlab-hq/cursor-advanced-rules.git"
        
        # 기존 원격 저장소 제거 후 재추가
        run_git(git_cmd, ["remote", "remove", "origin"], cwd=str(repo_dir))
        success, _, _ = run_git(git_cmd, ["remote", "add", "origin", remote_url], cwd=str(repo_dir))
        
        if success:
            print("✅ 보안 에이전트를 사용하여 인증 설정 완료")
            return True
        else:
            print("⚠️ 토큰 포함 URL 설정 실패, 수동 인증 필요")
            return False
    else:
        print("⚠️ GitHub 토큰이 없습니다. 수동 인증이 필요할 수 있습니다.")
        print("   토큰 설정 방법:")
        print("   python -c \"from scripts.security_agent_manager import get_security_agent; agent = get_security_agent(); agent.set_env_var('GITHUB_TOKEN', 'your_token', 'GitHub Personal Access Token')\"")
        return False

def main():
    """메인 함수"""
    print("🚀 GitHub 자동 푸시 (보안 에이전트 통합)...\n")
    
    # 보안 에이전트 상태 확인
    if SECURITY_AGENT_AVAILABLE:
        print("✅ 보안 에이전트 사용 가능\n")
    else:
        print("⚠️ 보안 에이전트 사용 불가 (수동 인증 필요)\n")
    
    # Git 찾기
    print("1️⃣ Git 경로 찾는 중...")
    git_cmd = find_git()
    
    if not git_cmd:
        print("❌ Git을 찾을 수 없습니다.")
        print("\n수동 실행 방법은 GIT_PUSH_MANUAL.md 참조")
        return 1
    
    print(f"✅ Git 발견: {git_cmd}\n")
    
    # 작업 디렉토리
    repo_dir = Path(__file__).parent
    os.chdir(repo_dir)
    print(f"📁 작업 디렉토리: {repo_dir}\n")
    
    # Git 초기화
    print("2️⃣ Git 초기화 중...")
    success, _, _ = run_git(git_cmd, ["init"], cwd=str(repo_dir))
    if not success:
        print("⚠️ Git 초기화 실패 (이미 초기화되었을 수 있음)")
    print()
    
    # 보안 에이전트로 인증 설정
    print("3️⃣ 보안 에이전트로 인증 설정 중...")
    setup_git_credentials(git_cmd, repo_dir)
    print()
    
    # 원격 저장소 확인/설정
    print("4️⃣ 원격 저장소 확인 중...")
    success, stdout, _ = run_git(git_cmd, ["remote", "-v"], cwd=str(repo_dir))
    
    if "origin" not in stdout:
        remote_url = "https://github.com/mkmlab-hq/cursor-advanced-rules.git"
        success, _, _ = run_git(git_cmd, ["remote", "add", "origin", remote_url], cwd=str(repo_dir))
        if not success:
            print("⚠️ 원격 저장소 추가 실패")
    else:
        print("✅ 원격 저장소 이미 설정됨")
    print()
    
    # 파일 추가
    print("5️⃣ 파일 추가 중...")
    success, _, _ = run_git(git_cmd, ["add", "."], cwd=str(repo_dir))
    if not success:
        print("❌ 파일 추가 실패")
        return 1
    print("✅ 파일 추가 완료\n")
    
    # 커밋
    print("6️⃣ 커밋 중...")
    commit_message = """Initial commit: 10 free rules + documentation

- Add 10 free rules (Priority 0-2)
- Add comprehensive documentation
- Add basic scripts (Python + PowerShell)
- Add MIT License
- Add contribution guidelines
- Add Pro Tier information"""
    
    success, _, _ = run_git(git_cmd, ["commit", "-m", commit_message], cwd=str(repo_dir))
    if not success:
        print("⚠️ 커밋 실패 (변경사항이 없을 수 있음)")
    print()
    
    # 브랜치 설정
    print("7️⃣ 브랜치 설정 중...")
    run_git(git_cmd, ["branch", "-M", "main"], cwd=str(repo_dir))
    print()
    
    # 푸시
    print("8️⃣ GitHub에 푸시 중...")
    success, stdout, stderr = run_git(git_cmd, ["push", "-u", "origin", "main"], cwd=str(repo_dir))
    
    if success:
        print("\n✅ 푸시 완료!")
        print(f"📦 Repository: https://github.com/mkmlab-hq/cursor-advanced-rules")
    else:
        print("\n❌ 푸시 실패")
        print("\n가능한 원인:")
        print("1. GitHub Personal Access Token이 설정되지 않음")
        print("2. 인증 실패")
        print("\n해결 방법:")
        print("1. 보안 에이전트로 토큰 설정:")
        print("   python -c \"from scripts.security_agent_manager import get_security_agent; agent = get_security_agent(); agent.set_env_var('GITHUB_TOKEN', 'your_token', 'GitHub PAT')\"")
        print("\n2. 또는 수동으로 푸시:")
        print(f"   cd {repo_dir}")
        print("   git push -u origin main")
        print("   (Username: mkmlab-hq, Password: [토큰])")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

