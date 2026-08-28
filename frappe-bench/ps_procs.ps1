Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -or $_.Name -eq 'gunicorn.exe' -or $_.Name -eq 'node.exe' -or $_.Name -eq 'redis-server.exe' } | ForEach-Object {
    $id = $_.ProcessId
    $cmd = $_.CommandLine
    Write-Output ("PID=$id CMD=$cmd")
}
