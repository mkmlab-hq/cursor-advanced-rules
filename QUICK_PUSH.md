# ⚡ 빠른 푸시 가이드

## 한 줄로 실행

```powershell
cd F:\workspace\.github-public; git init; git remote add origin https://github.com/mkmlab-hq/cursor-advanced-rules.git; git add .; git commit -m "Initial commit: 10 free rules + documentation"; git branch -M main; git push -u origin main
```

## 단계별 실행 (권장)

```powershell
# 1. 이동
cd F:\workspace\.github-public

# 2. 초기화
git init

# 3. 원격 추가
git remote add origin https://github.com/mkmlab-hq/cursor-advanced-rules.git

# 4. 파일 추가
git add .

# 5. 커밋
git commit -m "Initial commit: 10 free rules + documentation"

# 6. 푸시
git branch -M main
git push -u origin main
```

**인증 필요 시**: GitHub Personal Access Token 사용

