$exe = "C:\D3D\DREAM3D-6.5.168-Win64\PipelineRunner.exe"
$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_1x1x1_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_1x1x1_1.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_2x2x2_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_2x2x2_1.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_3x3x3_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_3x3x3_1.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_4x4x4_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_4x4x4_1.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_5x5x5_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_5x5x5_1.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_6x6x6_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_6x6x6_1.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_7x7x7_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_7x7x7_1.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_8x8x8_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_8x8x8_1.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_1x1x1_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_1x1x1_2.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_2x2x2_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_2x2x2_2.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_3x3x3_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_3x3x3_2.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_4x4x4_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_4x4x4_2.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_5x5x5_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_5x5x5_2.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_6x6x6_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_6x6x6_2.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_7x7x7_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_7x7x7_2.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_8x8x8_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_8x8x8_2.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60



$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_1x1x1_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_1x1x1_3.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_2x2x2_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_2x2x2_3.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_3x3x3_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_3x3x3_3.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_4x4x4_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_4x4x4_3.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_5x5x5_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_5x5x5_3.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_6x6x6_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_6x6x6_3.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_7x7x7_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_7x7x7_3.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile
Start-Sleep -Seconds 60

$pipeline = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_json\bench_8x8x8_with_seg.json"
$logfile = "C:\D3D\DREAM3D-6.5.168-Win64\bench\D3D_pipeline_log\D3D_log_8x8x8_3.txt"

& $exe -p $pipeline 2>&1 | ForEach-Object {
    $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    "$t $_"
} | Tee-Object -FilePath $logfile




