$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\llama.cpp'))
$art = 'D:\q5-strata-compare-20261111'
$build = 'D:\llama-ooc-p5-20261110\native-build'
$ggml = 'D:\llama-ooc-p0-p2-20261110\build\ggml\src'
$vs = 'C:\Program Files\Microsoft Visual Studio\18\Community'
New-Item -ItemType Directory -Path $art -Force | Out-Null
$batch = Join-Path $art 'build-probe.cmd'
$source = Join-Path $PSScriptRoot 'q5_probe.cpp'
$commands = @('@echo off', "call `"$vs\VC\Auxiliary\Build\vcvars64.bat`" -vcvars_ver=14.44 >nul", 'if errorlevel 1 exit /b 1')
$commands += "cl /nologo /std:c++17 /EHsc /O2 /MD /utf-8 /DGGML_SHARED /DLLAMA_SHARED /DNOMINMAX /I`"$repo\include`" /I`"$repo\src`" /I`"$repo\ggml\include`" `"$source`" /Fe:`"$art\q5_probe.exe`" /link /LIBPATH:`"$build\src`" /LIBPATH:`"$ggml`" llama.lib ggml.lib ggml-base.lib ggml-cpu.lib"
$commands += 'exit /b %errorlevel%'
[IO.File]::WriteAllLines($batch, $commands, [Text.UTF8Encoding]::new($false))
Push-Location $art
try { & $env:ComSpec /d /c "`"$batch`""; $result = $LASTEXITCODE } finally { Pop-Location }
if ($result -ne 0) { exit $result }
$packages = @{
  native = 'D:\llama-ooc-p5-20261110\native-bin'
  native_np = 'D:\llama-ooc-p5-20261110\native-noprefetch-bin'
  p6 = 'D:\llama-ooc-p6-20261110\file-bin'
}
foreach ($name in $packages.Keys) {
    $dest = Join-Path $art $name
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    Get-ChildItem -LiteralPath $packages[$name] -Filter '*.dll' | Copy-Item -Destination $dest
    Copy-Item -LiteralPath (Join-Path $art 'q5_probe.exe') -Destination $dest
}
