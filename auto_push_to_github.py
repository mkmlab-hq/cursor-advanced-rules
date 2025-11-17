#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 자동 푸시 스크립트
Git 경로를 자동으로 찾아서 푸시 수행
"""

import subprocess
import sys
import os
from pathlib import Path

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
                # PATH에서 찾기
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

def run_git(git_cmd, args, cwd=None):
    """Git 명령 실행"""
    try:
        full_cmd = [git_cmd] + args
        result = subprocess.run(
            full_cmd,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 GitHub 자동 푸시 시작...\n")
    
    # Git 찾기
    print("1️⃣ Git 경로 찾는 중...")
    git_cmd = find_git()
    
    if not git_cmd:
        print("❌ Git을 찾을 수 없습니다.")
        print("\n수동 실행 방법:")
        print("1. Git Bash 사용")
        print("2. 또는 다음 명령어를 직접 실행:")
        print("\n   cd F:\\workspace\\.github-public")
        print("   git init")
        print("   git remote add origin https://github.com/mkmlab-hq/cursor-advanced-rules.git")
        print("   git add .")
        print("   git commit -m \"Initial commit\"")
        print("   git branch -M main")
        print("   git push -u origin main")
        return 1
    
    print(f"✅ Git 발견: {git_cmd}\n")
    
    # 작업 디렉토리
    repo_dir = Path(__file__).parent
    os.chdir(repo_dir)
    print(f"📁 작업 디렉토리: {repo_dir}\n")
    
    # Git 초기화
    print("2️⃣ Git 초기화 중...")
    if not run_git(git_cmd, ["init"], cwd=str(repo_dir)):
        print("⚠️ Git 초기화 실패 (이미 초기화되었을 수 있음)")
    print()
    
    # 원격 저장소 추가
    print("3️⃣ 원격 저장소 추가 중...")
    remote_url = "https://github.com/mkmlab-hq/cursor-advanced-rules.git"
    
    # 기존 원격 저장소 확인
    result = subprocess.run(
        [git_cmd, "remote", "-v"],
        cwd=str(repo_dir),
        capture_output=True,
        text=True
    )
    
    if "origin" not in result.stdout:
        if not run_git(git_cmd, ["remote", "add", "origin", remote_url], cwd=str(repo_dir)):
            print("⚠️ 원격 저장소 추가 실패 (이미 추가되었을 수 있음)")
    else:
        print("✅ 원격 저장소 이미 설정됨")
    print()
    
    # 파일 추가
    print("4️⃣ 파일 추가 중...")
    if not run_git(git_cmd, ["add", "."], cwd=str(repo_dir)):
        print("❌ 파일 추가 실패")
        return 1
    print("✅ 파일 추가 완료\n")
    
    # 커밋
    print("5️⃣ 커밋 중...")
    commit_message = """Initial commit: 10 free rules + documentation

- Add 10 free rules (Priority 0-2)
- Add comprehensive documentation
- Add basic scripts (Python + PowerShell)
- Add MIT License
- Add contribution guidelines
- Add Pro Tier information"""
    
    if not run_git(git_cmd, ["commit", "-m", commit_message], cwd=str(repo_dir)):
        print("⚠️ 커밋 실패 (변경사항이 없을 수 있음)")
    print()
    
    # 브랜치 설정
    print("6️⃣ 브랜치 설정 중...")
    run_git(git_cmd, ["branch", "-M", "main"], cwd=str(repo_dir))
    print()
    
    # 푸시
    print("7️⃣ GitHub에 푸시 중...")
    print("⚠️ 인증이 필요할 수 있습니다.")
    print("   GitHub Personal Access Token을 사용하세요.\n")
    
    if not run_git(git_cmd, ["push", "-u", "origin", "main"], cwd=str(repo_dir)):
        print("\n❌ 푸시 실패")
        print("\n수동 실행 방법:")
        print(f"   cd {repo_dir}")
        print("   git push -u origin main")
        print("\n인증 필요 시:")
        print("   Username: mkmlab-hq")
        print("   Password: [GitHub Personal Access Token]")
        return 1
    
    print("\n✅ 푸시 완료!")
    print(f"📦 Repository: https://github.com/mkmlab-hq/cursor-advanced-rules")
    return 0

if __name__ == "__main__":
    sys.exit(main())

