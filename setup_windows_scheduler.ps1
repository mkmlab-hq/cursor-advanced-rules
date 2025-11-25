# Rules 자동 최적화 Windows 작업 스케줄러 등록 스크립트
# 주 1회 (매주 월요일 오전 9시) 자동 실행

$scriptPath = Join-Path $PSScriptRoot "rules_auto_cleanup_scheduler.py"
$pythonPath = "F:\Python311\python.exe"
$taskName = "RulesAutoCleanup"
$description = "Rules 자동 최적화 - 주 1회 실행 (미사용 룰 아카이브, 주간 리포트 생성)"

# 작업 스케줄러에 등록
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive

try {
    # 기존 작업이 있으면 삭제
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    
    # 새 작업 등록
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $description
    
    Write-Host "✅ 작업 스케줄러 등록 완료!" -ForegroundColor Green
    Write-Host "  작업 이름: $taskName" -ForegroundColor Cyan
    Write-Host "  실행 주기: 매주 월요일 오전 9시" -ForegroundColor Cyan
    Write-Host "  스크립트: $scriptPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "수동 실행: python `"$scriptPath`"" -ForegroundColor Yellow
    Write-Host "작업 확인: Get-ScheduledTask -TaskName $taskName" -ForegroundColor Yellow
    Write-Host "작업 삭제: Unregister-ScheduledTask -TaskName $taskName" -ForegroundColor Yellow
}
catch {
    Write-Host "❌ 작업 스케줄러 등록 실패: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "관리자 권한으로 실행하거나 수동으로 등록하세요:" -ForegroundColor Yellow
    Write-Host "  1. 작업 스케줄러 열기 (taskschd.msc)" -ForegroundColor Yellow
    Write-Host "  2. 기본 작업 만들기" -ForegroundColor Yellow
    Write-Host "  3. 트리거: 매주 월요일 오전 9시" -ForegroundColor Yellow
    Write-Host "  4. 작업: $pythonPath `"$scriptPath`"" -ForegroundColor Yellow
}

