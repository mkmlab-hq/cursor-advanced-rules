#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    Rules 파일 통계 리포트 생성

.DESCRIPTION
    Rules 파일의 통계 정보를 생성합니다.
    - 총 파일 수
    - Priority 분포
    - Type 분포
    - alwaysApply 분포
    - Globs/Tags 사용 현황
    - 메타데이터 완성도
    - 파일 크기 분석

.EXAMPLE
    .\rules-stats.ps1
    .\rules-stats.ps1 | Out-File report.txt
#>

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$rulesDir = Join-Path $PSScriptRoot "..\rules"
$rulesFiles = Get-ChildItem -Path $rulesDir -Filter "*.mdc" -ErrorAction SilentlyContinue

if (-not $rulesFiles) {
    Write-Host "❌ Rules 디렉토리를 찾을 수 없습니다: $rulesDir" -ForegroundColor Red
    exit 1
}

Write-Host "=== Rules Statistics Report ===" -ForegroundColor Cyan
Write-Host "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

$totalFiles = $rulesFiles.Count
Write-Host "📊 Total Rules: $totalFiles" -ForegroundColor Green
Write-Host ""

# Priority 분포
Write-Host "=== Priority Distribution ===" -ForegroundColor Cyan
$priorityCounts = @{}
foreach ($file in $rulesFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $priority = if ($content -match '(?m)^priority:\s*(\d+)') { 
        [int]$matches[1] 
    } else { 
        "N/A" 
    }
    
    if ($priority -ne "N/A") {
        if (-not $priorityCounts.ContainsKey($priority)) {
            $priorityCounts[$priority] = 0
        }
        $priorityCounts[$priority]++
    }
}

foreach ($p in 0, 1, 2, 3, 10) {
    $count = if ($priorityCounts.ContainsKey($p)) { $priorityCounts[$p] } else { 0 }
    Write-Host "Priority $p : $count files" -ForegroundColor White
}
Write-Host ""

# Type 분포
Write-Host "=== Type Distribution ===" -ForegroundColor Cyan
$typeCounts = @{}
foreach ($file in $rulesFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $type = if ($content -match '(?m)^type:\s*["'']?(\w+)["'']?') { 
        $matches[1] 
    } else { 
        "N/A" 
    }
    
    if (-not $typeCounts.ContainsKey($type)) {
        $typeCounts[$type] = 0
    }
    $typeCounts[$type]++
}

foreach ($t in "always", "intelligent", "file-specific", "manual") {
    $count = if ($typeCounts.ContainsKey($t)) { $typeCounts[$t] } else { 0 }
    Write-Host "Type '$t' : $count files" -ForegroundColor White
}
Write-Host ""

# alwaysApply 분포
Write-Host "=== AlwaysApply Distribution ===" -ForegroundColor Cyan
$alwaysTrue = 0
$alwaysFalse = 0
$alwaysNone = 0

foreach ($file in $rulesFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^alwaysApply:\s*(true|false)') {
        if ($matches[1] -eq "true") {
            $alwaysTrue++
        } else {
            $alwaysFalse++
        }
    } else {
        $alwaysNone++
    }
}

Write-Host "alwaysApply: true  → $alwaysTrue files" -ForegroundColor White
Write-Host "alwaysApply: false → $alwaysFalse files" -ForegroundColor White
Write-Host "alwaysApply: none  → $alwaysNone files" -ForegroundColor White
Write-Host ""

# Globs 사용
Write-Host "=== Globs Usage ===" -ForegroundColor Cyan
$globsCount = 0
foreach ($file in $rulesFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^globs:') {
        $globsCount++
    }
}
Write-Host "Files with globs: $globsCount / $totalFiles" -ForegroundColor White
Write-Host ""

# Tags 사용
Write-Host "=== Tags Usage ===" -ForegroundColor Cyan
$tagsCount = 0
foreach ($file in $rulesFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^tags:') {
        $tagsCount++
    }
}
Write-Host "Files with tags: $tagsCount / $totalFiles" -ForegroundColor White
Write-Host ""

# 메타데이터 완성도
Write-Host "=== Metadata Completeness ===" -ForegroundColor Cyan
$descCount = 0
$priorityCount = 0

foreach ($file in $rulesFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^description:') {
        $descCount++
    }
    if ($content -match '(?m)^priority:') {
        $priorityCount++
    }
}

Write-Host "Files with description: $descCount / $totalFiles" -ForegroundColor White
Write-Host "Files with priority: $priorityCount / $totalFiles" -ForegroundColor White
Write-Host ""

# 파일 크기 분석
Write-Host "=== File Size Analysis ===" -ForegroundColor Cyan
Write-Host "Top 5 largest files:" -ForegroundColor White
$filesWithSize = $rulesFiles | ForEach-Object {
    $lines = (Get-Content $_.FullName -Encoding UTF8).Count
    [PSCustomObject]@{
        Name = $_.Name
        Lines = $lines
        Size = $_.Length
    }
} | Sort-Object -Property Lines -Descending | Select-Object -First 5

foreach ($f in $filesWithSize) {
    Write-Host "  $($f.Name): $($f.Lines) lines ($([math]::Round($f.Size/1KB, 2)) KB)" -ForegroundColor Gray
}
Write-Host ""

# 500줄 초과 파일
Write-Host "=== Files Over 500 Lines ===" -ForegroundColor Cyan
$over500 = $rulesFiles | Where-Object {
    (Get-Content $_.FullName -Encoding UTF8).Count -gt 500
}

if ($over500) {
    foreach ($file in $over500) {
        $lines = (Get-Content $file.FullName -Encoding UTF8).Count
        Write-Host "⚠️  $($file.Name): $lines lines (consider splitting)" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ No files over 500 lines" -ForegroundColor Green
}

Write-Host ""

