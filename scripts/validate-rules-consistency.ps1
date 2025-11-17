#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    Rules 파일의 Type, Priority, alwaysApply 일치성 검증

.DESCRIPTION
    Cursor Rules 파일의 메타데이터 일관성을 검증합니다.
    - Priority 0 → type: "always", alwaysApply: true
    - Priority 10 → type: "manual", alwaysApply: false
    - Type "always" → alwaysApply: true
    - Type "manual" → alwaysApply: false

.EXAMPLE
    .\validate-rules-consistency.ps1
#>

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$rulesDir = Join-Path $PSScriptRoot "..\rules"
$rulesFiles = Get-ChildItem -Path $rulesDir -Filter "*.mdc" -ErrorAction SilentlyContinue

if (-not $rulesFiles) {
    Write-Host "❌ Rules 디렉토리를 찾을 수 없습니다: $rulesDir" -ForegroundColor Red
    exit 1
}

Write-Host "=== Rules Consistency Validation ===" -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

foreach ($file in $rulesFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # 메타데이터 추출
    $priority = if ($content -match '(?m)^priority:\s*(\d+)') { [int]$matches[1] } else { $null }
    $type = if ($content -match '(?m)^type:\s*["'']?(\w+)["'']?') { $matches[1] } else { $null }
    $alwaysApply = if ($content -match '(?m)^alwaysApply:\s*(true|false)') { $matches[1] -eq "true" } else { $null }
    
    $filename = $file.Name
    
    # Priority 0 검증
    if ($priority -eq 0) {
        if ($type -ne "always") {
            Write-Host "❌ ERROR: $filename" -ForegroundColor Red
            Write-Host "   Priority 0 but type is '$type' (should be 'always')" -ForegroundColor Yellow
            $errors++
        }
        if ($alwaysApply -ne $true) {
            Write-Host "❌ ERROR: $filename" -ForegroundColor Red
            Write-Host "   Priority 0 but alwaysApply is '$alwaysApply' (should be 'true')" -ForegroundColor Yellow
            $errors++
        }
    }
    
    # Priority 10 검증
    if ($priority -eq 10) {
        if ($type -ne "manual" -and $type -ne $null) {
            Write-Host "⚠️  WARNING: $filename" -ForegroundColor Yellow
            Write-Host "   Priority 10 but type is '$type' (consider 'manual')" -ForegroundColor Yellow
            $warnings++
        }
        if ($alwaysApply -ne $false -and $alwaysApply -ne $null) {
            Write-Host "❌ ERROR: $filename" -ForegroundColor Red
            Write-Host "   Priority 10 but alwaysApply is '$alwaysApply' (should be 'false')" -ForegroundColor Yellow
            $errors++
        }
    }
    
    # Type "always" 검증
    if ($type -eq "always") {
        if ($alwaysApply -ne $true -and $alwaysApply -ne $null) {
            Write-Host "⚠️  WARNING: $filename" -ForegroundColor Yellow
            Write-Host "   Type 'always' but alwaysApply is '$alwaysApply' (consider 'true')" -ForegroundColor Yellow
            $warnings++
        }
    }
    
    # Type "manual" 검증
    if ($type -eq "manual") {
        if ($alwaysApply -ne $false -and $alwaysApply -ne $null) {
            Write-Host "❌ ERROR: $filename" -ForegroundColor Red
            Write-Host "   Type 'manual' but alwaysApply is '$alwaysApply' (should be 'false')" -ForegroundColor Yellow
            $errors++
        }
    }
}

Write-Host ""
Write-Host "=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "Errors: $errors" -ForegroundColor $(if ($errors -eq 0) { "Green" } else { "Red" })
Write-Host "Warnings: $warnings" -ForegroundColor $(if ($warnings -eq 0) { "Green" } else { "Yellow" })

if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "✅ All rules are consistent!" -ForegroundColor Green
    exit 0
} else {
    exit 1
}

