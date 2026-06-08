$ErrorActionPreference = 'SilentlyContinue'
$outPath = 'e:\道\道生一\一生二\学习复习\_zhou_diag.txt'
$out = ''

function Append($s) { $script:out += $s + "`r`n" }

Append "═══ Windsurf · zhou vs Administrator · 全相察 · $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ═══"
Append ''

# ============================================================
# 一·当前 user / session 上下文
# ============================================================
Append '─── 一·当前上下文 ───'
Append "  whoami     : $(whoami)"
Append "  IsAdmin    : $(([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))"
Append "  COMPUTER   : $env:COMPUTERNAME"
Append ''

# qwinsta 看 sessions
Append '─── sessions (qwinsta) ───'
$qwOut = qwinsta 2>$null
$qwOut | Where-Object { $_ } | ForEach-Object { Append "  $_" }
Append ''

# ============================================================
# 二·E:\Windsurf · ext.js 真态 (二进制层血印)
# ============================================================
Append '─── 二·E:\Windsurf\ext.js 当下血印 ───'
$extJs = 'E:\Windsurf\resources\app\extensions\windsurf\dist\extension.js'
if (Test-Path $extJs) {
    $i = Get-Item $extJs
    Append "  size  = $($i.Length) B"
    Append "  mtime = $($i.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    $c = [System.IO.File]::ReadAllText($extJs)
    Append "  :8878         = $($c.Contains('127.0.0.1:8878'))"
    Append "  :8957         = $($c.Contains('127.0.0.1:8957'))"
    Append "  :11435        = $($c.Contains('127.0.0.1:11435'))"
    Append "  codeium.com   = $($c.Contains('server.codeium.com'))"
    Append "  self-serve    = $($c.Contains('self-serve.windsurf.com'))"
}
Append ''
Append '  ── 同目下 .bak 件 ──'
Get-ChildItem 'E:\Windsurf\resources\app\extensions\windsurf\dist' -Filter 'extension.js.bak*' -EA SilentlyContinue |
    Sort-Object Name | ForEach-Object {
        Append "    $($_.Name.PadRight(50)) $($_.Length)B  $($_.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))"
    }
Append ''

# ============================================================
# 三·当下所有 Windsurf / language_server 进程 · 按 owner 分布
# ============================================================
Append '─── 三·当下进程·owner 分布 ───'
$procs = Get-CimInstance Win32_Process -Filter "Name='Windsurf.exe'" -EA SilentlyContinue
$lsProcs = Get-CimInstance Win32_Process -EA SilentlyContinue | Where-Object { $_.Name -like 'language_server*' }
Append "  Windsurf.exe       总: $(($procs | Measure-Object).Count)"
Append "  language_server.*  总: $(($lsProcs | Measure-Object).Count)"
Append ''
Append '  ── Windsurf owner 分布 ──'
$ownerMap = @{}
foreach ($p in $procs) {
    $owner = '?'
    try {
        $oRes = Invoke-CimMethod -InputObject $p -MethodName GetOwner -EA SilentlyContinue
        if ($oRes -and $oRes.User) { $owner = "$($oRes.Domain)\$($oRes.User)" }
    } catch {}
    if (-not $ownerMap.ContainsKey($owner)) { $ownerMap[$owner] = 0 }
    $ownerMap[$owner]++
}
foreach ($k in $ownerMap.Keys | Sort-Object) {
    Append "    $($k.PadRight(40)) $($ownerMap[$k]) 进程"
}
Append ''

# Windsurf 顶层 (无 Windsurf 父) 主进程之 owner + session + user-data-dir
Append '  ── 顶层主进程 cmdline (无 Windsurf 父) ──'
foreach ($p in $procs) {
    $pp = $p.ParentProcessId
    $parent = Get-Process -Id $pp -EA SilentlyContinue
    $isTop = -not $parent -or $parent.Name -ne 'Windsurf'
    if ($isTop) {
        $owner = '?'
        try {
            $oRes = Invoke-CimMethod -InputObject $p -MethodName GetOwner -EA SilentlyContinue
            if ($oRes -and $oRes.User) { $owner = "$($oRes.Domain)\$($oRes.User)" }
        } catch {}
        $proc = Get-Process -Id $p.ProcessId -EA SilentlyContinue
        $sess = if ($proc) { $proc.SessionId } else { '?' }
        $start = if ($proc) { try { $proc.StartTime.ToString('MM-dd HH:mm:ss') } catch { '?' } } else { '?' }
        Append "    PID=$($p.ProcessId)  owner=$owner  Sess=$sess  Start=$start"
        $cl = $p.CommandLine
        if ($cl) {
            if ($cl.Length -gt 400) { $cl = $cl.Substring(0, 400) + '...' }
            Append "      cmd: $cl"
        }
    }
}
Append ''

# 找 gpu-process / renderer 之 user-data-dir
Append '  ── 子进程之 --user-data-dir (各 user 真用之 user-data) ──'
$udirs = @{}
foreach ($p in $procs) {
    if ($p.CommandLine -and $p.CommandLine -match '--user-data-dir="([^"]+)"') {
        $ud = $matches[1]
        $owner = '?'
        try {
            $oRes = Invoke-CimMethod -InputObject $p -MethodName GetOwner -EA SilentlyContinue
            if ($oRes -and $oRes.User) { $owner = "$($oRes.Domain)\$($oRes.User)" }
        } catch {}
        $key = "$owner || $ud"
        if (-not $udirs.ContainsKey($key)) { $udirs[$key] = 0 }
        $udirs[$key]++
    }
}
foreach ($k in $udirs.Keys | Sort-Object) {
    Append "    $k  · $($udirs[$k]) procs"
}
Append ''

# ============================================================
# 四·zhou session 真态 (有则察, 无则记)
# ============================================================
Append '─── 四·zhou 账号 windsurf 真态 ───'
$zhouProfile = 'C:\Users\zhou'
if (Test-Path $zhouProfile) {
    Append "  C:\Users\zhou 存"
    # zhou 之 Roaming\Windsurf
    $zhouUD = 'C:\Users\zhou\AppData\Roaming\Windsurf'
    if (Test-Path $zhouUD) {
        Append "  ── zhou\Roaming\Windsurf ──"
        $zhouSettings = "$zhouUD\User\settings.json"
        if (Test-Path $zhouSettings) {
            $si = Get-Item $zhouSettings
            Append "    settings.json: $($si.Length)B  mtime=$($si.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        }
        $zhouVscdb = "$zhouUD\User\globalStorage\state.vscdb"
        if (Test-Path $zhouVscdb) {
            $vi = Get-Item $zhouVscdb
            Append "    state.vscdb : $([Math]::Round($vi.Length/1KB,1))KB  mtime=$($vi.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        }
        # auth 文件
        $zhouAuth = "$zhouUD\User\globalStorage\windsurf-auth.json"
        if (Test-Path $zhouAuth) {
            $ai = Get-Item $zhouAuth
            Append "    windsurf-auth.json: $($ai.Length)B  mtime=$($ai.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        } else {
            Append "    windsurf-auth.json: 无"
        }
        $zhouCAuth = "$zhouUD\User\globalStorage\cascade-auth.json"
        if (Test-Path $zhouCAuth) {
            $ai = Get-Item $zhouCAuth
            Append "    cascade-auth.json : $($ai.Length)B  mtime=$($ai.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        } else {
            Append "    cascade-auth.json : 无"
        }
        # 最新 log dir
        $zhouLogs = "$zhouUD\logs"
        if (Test-Path $zhouLogs) {
            $latest = Get-ChildItem $zhouLogs -Directory -EA SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3
            Append "    ── 最近 3 logs dir ──"
            foreach ($d in $latest) {
                Append "      $($d.Name)  mtime=$($d.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
            }
            # 最新 dir 内核心 log 大小
            if ($latest) {
                $d = $latest[0]
                Append "    ── 最新 dir [$($d.Name)] 关键 log ──"
                $keyLogs = @(
                    "$($d.FullName)\main.log",
                    "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf ACP.log",
                    "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf.log",
                    "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf (Lifeguard).log"
                )
                foreach ($lf in $keyLogs) {
                    if (Test-Path $lf) {
                        $li = Get-Item $lf
                        Append "      $($lf.Substring($d.FullName.Length+1)) · $($li.Length)B · $($li.LastWriteTime.ToString('HH:mm:ss'))"
                    }
                }
                # WAM log
                $wamLog = Get-ChildItem "$($d.FullName)\window1\exthost\output_logging_*" -Filter '*WAM.log' -Recurse -EA SilentlyContinue | Select-Object -First 1
                if ($wamLog) {
                    Append "      WAM.log path: $($wamLog.FullName.Substring($d.FullName.Length+1))"
                    Append "      WAM.log     : $($wamLog.Length)B  mtime=$($wamLog.LastWriteTime.ToString('HH:mm:ss'))"
                }
            }
        }
    } else {
        Append "  ✗ zhou\Roaming\Windsurf 不存"
    }
    # zhou 之 .wam
    Append ''
    $zhouWam = 'C:\Users\zhou\.wam'
    if (Test-Path $zhouWam) {
        Append "  ── zhou\.wam ──"
        $am = "$zhouWam\accounts.md"
        if (Test-Path $am) {
            $ami = Get-Item $am
            Append "    accounts.md   : $($ami.Length)B  mtime=$($ami.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        }
        $ws = "$zhouWam\wam-state.json"
        if (Test-Path $ws) {
            $wi = Get-Item $ws
            Append "    wam-state.json: $($wi.Length)B  mtime=$($wi.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        }
        $wl = "$zhouWam\wam.log"
        if (Test-Path $wl) {
            $wli = Get-Item $wl
            Append "    wam.log       : $([Math]::Round($wli.Length/1KB,1))KB  mtime=$($wli.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        }
    } else {
        Append "  ✗ zhou\.wam 不存"
    }
    # zhou 之 .windsurf
    Append ''
    $zhouWindsurf = 'C:\Users\zhou\.windsurf'
    if (Test-Path $zhouWindsurf) {
        Append "  ── zhou\.windsurf ──"
        $exts = Get-ChildItem "$zhouWindsurf\extensions" -Directory -EA SilentlyContinue
        Append "    extensions 子目: $(($exts | Measure-Object).Count)"
        $wamExt = $exts | Where-Object { $_.Name -match 'rt-flow|wam' }
        foreach ($w in $wamExt) {
            Append "      ★ $($w.Name) · mtime=$($w.LastWriteTime.ToString('MM-dd HH:mm'))"
        }
    } else {
        Append "  ✗ zhou\.windsurf 不存"
    }
} else {
    Append "  ✗ C:\Users\zhou 不存 · zhou 账号无 profile"
}
Append ''

# ============================================================
# 五·administer (主公) windsurf 真态 (作 working baseline)
# ============================================================
Append '─── 五·Administrator (主公) windsurf 真态 ───'
$adminProfile = 'C:\Users\Administrator'
if (Test-Path $adminProfile) {
    Append "  C:\Users\Administrator 存"
    $adminUD = 'C:\Users\Administrator\AppData\Roaming\Windsurf'
    if (Test-Path $adminUD) {
        Append "  ── Administrator\Roaming\Windsurf ──"
        $set = "$adminUD\User\settings.json"
        if (Test-Path $set) {
            $si = Get-Item $set
            Append "    settings.json: $($si.Length)B  mtime=$($si.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        }
        $db = "$adminUD\User\globalStorage\state.vscdb"
        if (Test-Path $db) {
            $vi = Get-Item $db
            Append "    state.vscdb : $([Math]::Round($vi.Length/1KB,1))KB  mtime=$($vi.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        }
        $auth = "$adminUD\User\globalStorage\windsurf-auth.json"
        if (Test-Path $auth) {
            $ai = Get-Item $auth
            Append "    windsurf-auth.json: $($ai.Length)B  mtime=$($ai.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        } else {
            Append "    windsurf-auth.json: 无"
        }
        $cauth = "$adminUD\User\globalStorage\cascade-auth.json"
        if (Test-Path $cauth) {
            $ai = Get-Item $cauth
            Append "    cascade-auth.json : $($ai.Length)B  mtime=$($ai.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        } else {
            Append "    cascade-auth.json : 无"
        }
        $adminLogs = "$adminUD\logs"
        if (Test-Path $adminLogs) {
            $latest = Get-ChildItem $adminLogs -Directory -EA SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3
            Append "    ── 最近 3 logs dir ──"
            foreach ($d in $latest) {
                Append "      $($d.Name)  mtime=$($d.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
            }
            if ($latest) {
                $d = $latest[0]
                Append "    ── 最新 dir [$($d.Name)] 关键 log ──"
                $keyLogs = @(
                    "$($d.FullName)\main.log",
                    "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf ACP.log",
                    "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf.log",
                    "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf (Lifeguard).log"
                )
                foreach ($lf in $keyLogs) {
                    if (Test-Path $lf) {
                        $li = Get-Item $lf
                        Append "      $($lf.Substring($d.FullName.Length+1)) · $($li.Length)B · $($li.LastWriteTime.ToString('HH:mm:ss'))"
                    }
                }
                $wamLog = Get-ChildItem "$($d.FullName)\window1\exthost\output_logging_*" -Filter '*WAM.log' -Recurse -EA SilentlyContinue | Select-Object -First 1
                if ($wamLog) {
                    Append "      WAM.log     : $($wamLog.Length)B  mtime=$($wamLog.LastWriteTime.ToString('HH:mm:ss'))"
                }
            }
        }
    } else {
        Append "  ✗ Administrator\Roaming\Windsurf 不存"
    }
    # admin .wam
    Append ''
    $adminWam = 'C:\Users\Administrator\.wam'
    if (Test-Path $adminWam) {
        Append "  ── Administrator\.wam ──"
        $am = "$adminWam\accounts.md"
        if (Test-Path $am) {
            $ami = Get-Item $am
            Append "    accounts.md   : $($ami.Length)B  mtime=$($ami.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        }
        $ws = "$adminWam\wam-state.json"
        if (Test-Path $ws) {
            $wi = Get-Item $ws
            Append "    wam-state.json: $($wi.Length)B  mtime=$($wi.LastWriteTime.ToString('MM-dd HH:mm:ss'))"
        }
    } else {
        Append "  ✗ Administrator\.wam 不存"
    }
} else {
    Append "  ✗ C:\Users\Administrator 不存"
}
Append ''

# ============================================================
# 六·查看本机 C:\Users 各 profile 是否还有 zhouyoukang
# ============================================================
Append '─── 六·本机各 user profile 一览 ───'
Get-ChildItem 'C:\Users' -Directory -EA SilentlyContinue | Sort-Object Name | ForEach-Object {
    $wsLog = Join-Path $_.FullName 'AppData\Roaming\Windsurf\logs'
    $hasWs = Test-Path $wsLog
    $line = "  $($_.Name.PadRight(25))  hasWindsurfLogs=$hasWs"
    if ($hasWs) {
        $latest = Get-ChildItem $wsLog -Directory -EA SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($latest) {
            $line += "  latest=$($latest.Name) mtime=$($latest.LastWriteTime.ToString('MM-dd HH:mm'))"
        }
    }
    Append $line
}
Append ''

# ============================================================
# 七·网络真态·:8878 listener + outbound + 官方真出向
# ============================================================
Append '─── 七·网络真态 ───'
foreach ($port in 8878, 8957, 11435) {
    $l = Get-NetTCPConnection -LocalPort $port -State Listen -EA SilentlyContinue
    if ($l) {
        $proc = Get-Process -Id $l[0].OwningProcess -EA SilentlyContinue
        Append "  :$port  LISTENING  PID=$($l[0].OwningProcess) name=$($proc.Name)"
    } else {
        Append "  :$port  no listener"
    }
}
Append ''
$c8878 = Get-NetTCPConnection -RemotePort 8878 -EA SilentlyContinue
Append "  outbound :8878 = $(($c8878 | Measure-Object).Count)"
Append ''
Append '  ── Windsurf/LS 之真出向官方 ──'
$wsConns = Get-NetTCPConnection -State Established -EA SilentlyContinue | Where-Object {
    $proc = Get-Process -Id $_.OwningProcess -EA SilentlyContinue
    $proc -and ($proc.Name -eq 'Windsurf' -or $proc.Name -like 'language_server*') -and
    $_.RemoteAddress -notmatch '^(127\.|192\.168\.|10\.|172\.|::1|169\.254|fe80|0\.0\.0\.0)'
}
if ($wsConns) {
    $wsConns | Group-Object RemoteAddress, RemotePort | ForEach-Object {
        $first = $_.Group[0]
        $proc = Get-Process -Id $first.OwningProcess -EA SilentlyContinue
        Append "    $($first.RemoteAddress):$($first.RemotePort) ← $($_.Count) · $($proc.Name)"
    }
} else {
    Append '    无'
}
Append ''

# ============================================================
# 八·schtasks 关 dao/Wam/Windsurf
# ============================================================
Append '─── 八·schtasks (zhou launch + WAM 系) ───'
$tasks = schtasks /Query /FO CSV 2>$null | ConvertFrom-Csv -EA SilentlyContinue | Where-Object {
    $_.TaskName -match 'Dao|dao|Wam|wam|Windsurf|windsurf|Zhou|zhou' -and $_.TaskName -notmatch '^\\Microsoft'
}
if ($tasks) {
    foreach ($t in $tasks) {
        Append "  $($t.TaskName.PadRight(30))  Status=$($t.Status)  Next=$($t.'Next Run Time')"
    }
} else {
    Append '  (无)'
}
Append ''

Append "═══ 察相完成 · $(Get-Date -Format 'HH:mm:ss') ═══"

# 写文件
[System.IO.File]::WriteAllText($outPath, $out, [System.Text.UTF8Encoding]::new($false))
Write-Output "OK · $outPath · $($out.Length) chars"
