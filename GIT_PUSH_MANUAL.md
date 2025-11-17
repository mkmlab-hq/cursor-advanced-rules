# 🚀 Git 푸시 수동 실행 가이드

**상황**: Git이 PATH에 없거나 자동 실행이 실패한 경우

---

## 📋 수동 실행 명령어

### PowerShell에서 실행

```powershell
# 1. 디렉토리 이동
cd F:\workspace\.github-public

# 2. Git 초기화
git init

# 3. 원격 저장소 추가
git remote add origin https://github.com/mkmlab-hq/cursor-advanced-rules.git

# 4. 사용자 정보 설정 (한 번만)
git config user.name "mkmlab-hq"
git config user.email "mkmlab-hq@users.noreply.github.com"

# 5. 모든 파일 추가
git add .

# 6. 커밋
git commit -m "Initial commit: 10 free rules + documentation

- Add 10 free rules (Priority 0-2)
- Add comprehensive documentation
- Add basic scripts (Python + PowerShell)
- Add MIT License
- Add contribution guidelines
- Add Pro Tier information"

# 7. 메인 브랜치로 설정 및 푸시
git branch -M main
git push -u origin main
```

---

## 🔐 인증 필요 시

### Personal Access Token 사용

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. 권한: `repo` 체크
4. 생성된 토큰 복사

### 푸시 시 토큰 사용

```powershell
# 토큰을 사용하여 푸시
git push -u origin main
# Username: mkmlab-hq
# Password: [생성한 토큰 입력]
```

또는:

```powershell
# URL에 토큰 포함
git remote set-url origin https://YOUR_TOKEN@github.com/mkmlab-hq/cursor-advanced-rules.git
git push -u origin main
```

---

## ✅ 확인

푸시 후 GitHub에서 확인:
- https://github.com/mkmlab-hq/cursor-advanced-rules

다음 파일들이 보여야 함:
- ✅ README.md
- ✅ LICENSE
- ✅ rules/ (10개 파일)
- ✅ scripts/ (4개 파일)
- ✅ docs/ (5개 파일)

---

**준비된 파일이 모두 있으니, 위 명령어를 직접 실행하시면 됩니다!** 🚀

