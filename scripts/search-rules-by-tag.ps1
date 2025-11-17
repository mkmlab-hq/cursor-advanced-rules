#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    Tags로 Rules 검색

.DESCRIPTION
    지정된 태그(들)를 포함하는 Rules 파일을 검색합니다.
    여러 태그를 지정하면 모든 태그가 포함된 파일만 검색합니다 (AND 검색).

.PARAMETER Tags
    검색할 태그 목록

.EXAMPLE
    .\search-rules-by-tag.ps1 critical
    .\search-rules-by-tag.ps1 critical f-drive
    .\search-rules-by-tag.ps1 personality
#>

param(
    [Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)]
    [string[]]$Tags
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if ($Tags.Count -eq 0) {
    Write-Host "Usage: .\search-rules-by-tag.ps1 <tag> [tag2] [tag3]..." -ForegroundColor Yellow
    Write-Host "Example: .\search-rules-by-tag.ps1 critical" -ForegroundColor Yellow
    Write-Host "Example: .\search-rules-by-tag.ps1 critical f-drive" -ForegroundColor Yellow
    exit 1
}

$rulesDir = Join-Path $PSScriptRoot "..\rules"
$rulesFiles = Get-ChildItem -Path $rulesDir -Filter "*.mdc" -ErrorAction SilentlyContinue

if (-not $rulesFiles) {
    Write-Host "❌ Rules 디렉토리를 찾을 수 없습니다: $rulesDir" -ForegroundColor Red
    exit 1
}

Write-Host "=== Searching Rules by Tags ===" -ForegroundColor Cyan
Write-Host "Tags: $($Tags -join ', ')" -ForegroundColor Cyan
Write-Host ""

$found = 0

foreach ($file in $rulesFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # Tags 라인 추출
    $tagsLine = if ($content -match '(?m)^tags:\s*\[(.*?)\]') { $matches[1] } else { "" }
    
    if ([string]::IsNullOrWhiteSpace($tagsLine)) {
        continue
    }
    
    # 모든 태그가 포함되어 있는지 확인
    $allMatch = $true
    foreach ($tag in $Tags) {
        if ($tagsLine -notmatch $tag) {
            $allMatch = $false
            break
        }
    }
    
    if ($allMatch) {
        $found++
        $filename = $file.Name
        
        # 메타데이터 추출
        $priority = if ($content -match '(?m)^priority:\s*(\d+)') { $matches[1] } else { "N/A" }
        $type = if ($content -match '(?m)^type:\s*["'']?(\w+)["'']?') { $matches[1] } else { "N/A" }
        $description = if ($content -match '(?m)^description:\s*(.+?)(?:\n|$)') { $matches[1].Trim() } else { "N/A" }
        
        Write-Host "📄 $filename" -ForegroundColor Green
        Write-Host "   Priority: $priority | Type: $type" -ForegroundColor Cyan
        Write-Host "   $description" -ForegroundColor White
        Write-Host "   Tags: $tagsLine" -ForegroundColor Gray
        Write-Host ""
    }
}

if ($found -eq 0) {
    Write-Host "⚠️  No rules found with tags: $($Tags -join ', ')" -ForegroundColor Yellow
} else {
    Write-Host "✅ Found $found rule(s)" -ForegroundColor Green
}

