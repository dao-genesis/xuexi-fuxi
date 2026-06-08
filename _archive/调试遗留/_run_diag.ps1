$ErrorActionPreference = 'SilentlyContinue'
$body = @'
$ErrorActionPreference = 'SilentlyContinue'
$outPath = 'e:\dao_sheng_yi\zhou_diag.txt'
$out = New-Object System.Text.StringBuilder

function W($s){ [void]$out.AppendLine($s) }

W "=== Windsurf zhou vs Administrator diag === $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
W ""

# 1. ctx
W "--- 1. CTX ---"
W "  whoami     : $(whoami)"
W "  IsAdmin    : $(([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))"
W "  COMPUTER   : $env:COMPUTERNAME"
W ""

W "--- sessions ---"
(qwinsta 2>$null) | Where-Object { $_ } | ForEach-Object { W ("  " + $_) }
W ""

# 2. E:\Windsurf ext.js
W "--- 2. E:\Windsurf ext.js ---"
$extJs = 'E:\Windsurf\resources\app\extensions\windsurf\dist\extension.js'
if(Test-Path $extJs){
  $i = Get-Item $extJs
  W "  size  = $($i.Length) B"
  W "  mtime = $($i.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))"
  $c = [System.IO.File]::ReadAllText($extJs)
  W "  has 8878         = $($c.Contains('127.0.0.1:8878'))"
  W "  has 8957         = $($c.Contains('127.0.0.1:8957'))"
  W "  has 11435        = $($c.Contains('127.0.0.1:11435'))"
  W "  has codeium.com  = $($c.Contains('server.codeium.com'))"
  W "  has self-serve   = $($c.Contains('self-serve.windsurf.com'))"
} else { W "  NOT FOUND" }
W "  -- .bak files --"
Get-ChildItem 'E:\Windsurf\resources\app\extensions\windsurf\dist' -Filter 'extension.js.bak*' -EA SilentlyContinue |
    Sort-Object Name | ForEach-Object {
        W ("    " + $_.Name.PadRight(50) + " " + $_.Length + "B  " + $_.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))
    }
W ""

# 3. processes
W "--- 3. processes ---"
$procs = Get-CimInstance Win32_Process -Filter "Name='Windsurf.exe'" -EA SilentlyContinue
$lsProcs = Get-CimInstance Win32_Process -EA SilentlyContinue | Where-Object { $_.Name -like 'language_server*' }
W "  Windsurf.exe       count: $(($procs | Measure-Object).Count)"
W "  language_server.*  count: $(($lsProcs | Measure-Object).Count)"
W ""
W "  -- owner distribution --"
$ownerMap = @{}
foreach($p in $procs){
  $owner = 'unknown'
  try {
    $oRes = Invoke-CimMethod -InputObject $p -MethodName GetOwner -EA SilentlyContinue
    if($oRes -and $oRes.User){ $owner = "$($oRes.Domain)\$($oRes.User)" }
  } catch {}
  if(-not $ownerMap.ContainsKey($owner)){ $ownerMap[$owner] = 0 }
  $ownerMap[$owner]++
}
foreach($k in $ownerMap.Keys | Sort-Object){
  W ("    " + $k.PadRight(40) + " " + $ownerMap[$k] + " procs")
}
W ""

# 4. top main windsurf cmdline
W "  -- top main windsurf cmdline --"
$pat = '--user-data-dir="([^"]+)"'
foreach($p in $procs){
  $pp = $p.ParentProcessId
  $parent = Get-Process -Id $pp -EA SilentlyContinue
  $isTop = -not $parent -or $parent.Name -ne 'Windsurf'
  if($isTop){
    $owner = 'unknown'
    try {
      $oRes = Invoke-CimMethod -InputObject $p -MethodName GetOwner -EA SilentlyContinue
      if($oRes -and $oRes.User){ $owner = "$($oRes.Domain)\$($oRes.User)" }
    } catch {}
    $proc = Get-Process -Id $p.ProcessId -EA SilentlyContinue
    $sess = if($proc){$proc.SessionId}else{'?'}
    $start = if($proc){ try{$proc.StartTime.ToString('MM-dd HH:mm:ss')}catch{'?'} }else{'?'}
    W ("    PID=$($p.ProcessId)  owner=$owner  Sess=$sess  Start=$start")
    $cl = $p.CommandLine
    if($cl){
      if($cl.Length -gt 350){ $cl = $cl.Substring(0,350) + '...' }
      W ("      cmd: " + $cl)
    }
  }
}
W ""

# 5. user-data-dir per owner
W "  -- user-data-dir per owner --"
$udirs = @{}
foreach($p in $procs){
  if($p.CommandLine -and ($p.CommandLine -match $pat)){
    $ud = $matches[1]
    $owner = 'unknown'
    try {
      $oRes = Invoke-CimMethod -InputObject $p -MethodName GetOwner -EA SilentlyContinue
      if($oRes -and $oRes.User){ $owner = "$($oRes.Domain)\$($oRes.User)" }
    } catch {}
    $key = "$owner :: $ud"
    if(-not $udirs.ContainsKey($key)){ $udirs[$key] = 0 }
    $udirs[$key]++
  }
}
foreach($k in $udirs.Keys | Sort-Object){
  W ("    " + $k + "  x " + $udirs[$k])
}
W ""

# 6. zhou data
W "--- 4. zhou windsurf state ---"
$zhouProfile = 'C:\Users\zhou'
if(Test-Path $zhouProfile){
  W "  C:\Users\zhou exists"
  $zhouUD = 'C:\Users\zhou\AppData\Roaming\Windsurf'
  if(Test-Path $zhouUD){
    W "  -- zhou Roaming Windsurf --"
    foreach($name in 'User\settings.json','User\globalStorage\state.vscdb','User\globalStorage\windsurf-auth.json','User\globalStorage\cascade-auth.json'){
      $f = Join-Path $zhouUD $name
      if(Test-Path $f){
        $fi = Get-Item $f
        W ("    " + $name.PadRight(48) + " " + $fi.Length + "B  " + $fi.LastWriteTime.ToString('MM-dd HH:mm:ss'))
      } else {
        W ("    " + $name.PadRight(48) + " MISSING")
      }
    }
    $zhouLogs = "$zhouUD\logs"
    if(Test-Path $zhouLogs){
      $latest = Get-ChildItem $zhouLogs -Directory -EA SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3
      W "    -- recent 3 logs dir --"
      foreach($d in $latest){
        W ("      " + $d.Name + "  mtime=" + $d.LastWriteTime.ToString('MM-dd HH:mm:ss'))
      }
      if($latest){
        $d = $latest[0]
        W ("    -- latest [" + $d.Name + "] key logs --")
        foreach($lf in @(
            "$($d.FullName)\main.log",
            "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf ACP.log",
            "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf.log",
            "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf (Lifeguard).log"
        )){
          if(Test-Path $lf){
            $li = Get-Item $lf
            W ("      " + $lf.Substring($d.FullName.Length+1) + " : " + $li.Length + "B  " + $li.LastWriteTime.ToString('HH:mm:ss'))
          }
        }
        $wamLog = Get-ChildItem "$($d.FullName)\window1\exthost\output_logging_*" -Filter '*WAM.log' -Recurse -EA SilentlyContinue | Select-Object -First 1
        if($wamLog){
          W ("      WAM.log : " + $wamLog.Length + "B  " + $wamLog.LastWriteTime.ToString('HH:mm:ss'))
          W ("      WAM path: " + $wamLog.FullName.Substring($d.FullName.Length+1))
        }
      }
    }
  } else { W "  X zhou Roaming Windsurf MISSING" }
  W ""
  $zhouWam = 'C:\Users\zhou\.wam'
  if(Test-Path $zhouWam){
    W "  -- zhou .wam --"
    foreach($name in 'accounts.md','wam-state.json','wam.log'){
      $f = Join-Path $zhouWam $name
      if(Test-Path $f){
        $fi = Get-Item $f
        W ("    " + $name.PadRight(20) + " " + $fi.Length + "B  " + $fi.LastWriteTime.ToString('MM-dd HH:mm:ss'))
      } else {
        W ("    " + $name.PadRight(20) + " MISSING")
      }
    }
  } else { W "  X zhou .wam MISSING" }
  W ""
  $zhouWindsurf = 'C:\Users\zhou\.windsurf'
  if(Test-Path $zhouWindsurf){
    W "  -- zhou .windsurf --"
    $exts = Get-ChildItem "$zhouWindsurf\extensions" -Directory -EA SilentlyContinue
    W ("    extensions count: " + (($exts | Measure-Object).Count))
    $wamExt = $exts | Where-Object { $_.Name -match 'rt-flow|wam' }
    foreach($w in $wamExt){
      W ("      * " + $w.Name + " mtime=" + $w.LastWriteTime.ToString('MM-dd HH:mm'))
    }
  } else { W "  X zhou .windsurf MISSING" }
} else { W "  X C:\Users\zhou not found" }
W ""

# 7. administrator data
W "--- 5. Administrator windsurf state (baseline) ---"
$adminProfile = 'C:\Users\Administrator'
if(Test-Path $adminProfile){
  $adminUD = 'C:\Users\Administrator\AppData\Roaming\Windsurf'
  if(Test-Path $adminUD){
    W "  -- Admin Roaming Windsurf --"
    foreach($name in 'User\settings.json','User\globalStorage\state.vscdb','User\globalStorage\windsurf-auth.json','User\globalStorage\cascade-auth.json'){
      $f = Join-Path $adminUD $name
      if(Test-Path $f){
        $fi = Get-Item $f
        W ("    " + $name.PadRight(48) + " " + $fi.Length + "B  " + $fi.LastWriteTime.ToString('MM-dd HH:mm:ss'))
      } else {
        W ("    " + $name.PadRight(48) + " MISSING")
      }
    }
    $adminLogs = "$adminUD\logs"
    if(Test-Path $adminLogs){
      $latest = Get-ChildItem $adminLogs -Directory -EA SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3
      W "    -- recent 3 logs dir --"
      foreach($d in $latest){
        W ("      " + $d.Name + "  mtime=" + $d.LastWriteTime.ToString('MM-dd HH:mm:ss'))
      }
      if($latest){
        $d = $latest[0]
        W ("    -- latest [" + $d.Name + "] key logs --")
        foreach($lf in @(
            "$($d.FullName)\main.log",
            "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf ACP.log",
            "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf.log",
            "$($d.FullName)\window1\exthost\codeium.windsurf\Windsurf (Lifeguard).log"
        )){
          if(Test-Path $lf){
            $li = Get-Item $lf
            W ("      " + $lf.Substring($d.FullName.Length+1) + " : " + $li.Length + "B  " + $li.LastWriteTime.ToString('HH:mm:ss'))
          }
        }
        $wamLog = Get-ChildItem "$($d.FullName)\window1\exthost\output_logging_*" -Filter '*WAM.log' -Recurse -EA SilentlyContinue | Select-Object -First 1
        if($wamLog){
          W ("      WAM.log : " + $wamLog.Length + "B  " + $wamLog.LastWriteTime.ToString('HH:mm:ss'))
        }
      }
    }
  } else { W "  X Admin Roaming Windsurf MISSING" }
  W ""
  $adminWam = 'C:\Users\Administrator\.wam'
  if(Test-Path $adminWam){
    W "  -- Admin .wam --"
    foreach($name in 'accounts.md','wam-state.json','wam.log'){
      $f = Join-Path $adminWam $name
      if(Test-Path $f){
        $fi = Get-Item $f
        W ("    " + $name.PadRight(20) + " " + $fi.Length + "B  " + $fi.LastWriteTime.ToString('MM-dd HH:mm:ss'))
      } else {
        W ("    " + $name.PadRight(20) + " MISSING")
      }
    }
  } else { W "  X Admin .wam MISSING" }
} else { W "  X C:\Users\Administrator not found" }
W ""

# 8. all profiles
W "--- 6. all user profiles ---"
Get-ChildItem 'C:\Users' -Directory -EA SilentlyContinue | Sort-Object Name | ForEach-Object {
  $wsLog = Join-Path $_.FullName 'AppData\Roaming\Windsurf\logs'
  $hasWs = Test-Path $wsLog
  $line = "  " + $_.Name.PadRight(25) + " hasWindsurfLogs=" + $hasWs
  if($hasWs){
    $latest = Get-ChildItem $wsLog -Directory -EA SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if($latest){
      $line += "  latest=" + $latest.Name + " mtime=" + $latest.LastWriteTime.ToString('MM-dd HH:mm')
    }
  }
  W $line
}
W ""

# 9. network
W "--- 7. network ---"
foreach($port in 8878,8957,11435){
  $l = Get-NetTCPConnection -LocalPort $port -State Listen -EA SilentlyContinue
  if($l){
    $proc = Get-Process -Id $l[0].OwningProcess -EA SilentlyContinue
    W ("  :$port  LISTENING  PID=$($l[0].OwningProcess) name=$($proc.Name)")
  } else {
    W ("  :$port  no listener")
  }
}
W ""
$c8878 = Get-NetTCPConnection -RemotePort 8878 -EA SilentlyContinue
W ("  outbound :8878 = " + (($c8878 | Measure-Object).Count))
W ""
W "  -- Windsurf/LS outbound official --"
$wsConns = Get-NetTCPConnection -State Established -EA SilentlyContinue | Where-Object {
  $proc = Get-Process -Id $_.OwningProcess -EA SilentlyContinue
  $proc -and ($proc.Name -eq 'Windsurf' -or $proc.Name -like 'language_server*') -and
  $_.RemoteAddress -notmatch '^(127\.|192\.168\.|10\.|172\.|::1|169\.254|fe80|0\.0\.0\.0)'
}
if($wsConns){
  $wsConns | Group-Object RemoteAddress,RemotePort | ForEach-Object {
    $first = $_.Group[0]
    $proc = Get-Process -Id $first.OwningProcess -EA SilentlyContinue
    W ("    " + $first.RemoteAddress + ":" + $first.RemotePort + " x " + $_.Count + " name=" + $proc.Name)
  }
} else { W "    none" }
W ""

# 10. schtasks
W "--- 8. schtasks (zhou/wam/dao) ---"
$tasks = schtasks /Query /FO CSV 2>$null | ConvertFrom-Csv -EA SilentlyContinue | Where-Object {
  $_.TaskName -match 'Dao|dao|Wam|wam|Windsurf|windsurf|Zhou|zhou' -and $_.TaskName -notmatch '^\\Microsoft'
}
if($tasks){
  foreach($t in $tasks){
    W ("  " + $t.TaskName.PadRight(35) + " Status=" + $t.Status + " Next=" + $t.'Next Run Time')
  }
} else { W "  (none)" }
W ""

W "=== diag done $(Get-Date -Format 'HH:mm:ss') ==="

# write file
$dir = Split-Path $outPath
if(-not (Test-Path $dir)){ New-Item -ItemType Directory -Path $dir -Force | Out-Null }
[System.IO.File]::WriteAllText($outPath, $out.ToString(), [System.Text.UTF8Encoding]::new($false))
Write-Output "OK : $outPath : $($out.Length) chars"
'@

$b64 = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($body))
powershell -NoProfile -EncodedCommand $b64
