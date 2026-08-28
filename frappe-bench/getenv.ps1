$uv = [Environment]::GetEnvironmentVariables('User')
$mv = [Environment]::GetEnvironmentVariables('Machine')
$all = $uv + $mv
$all.GetEnumerator() | Where-Object { $_.Key -match 'pass|db_|postgres|pg|hindsight|database|frappe' -or $_.Value -match 'postgres|5432|site1_local' } | ForEach-Object { "$($_.Key)=$($_.Value)" }
