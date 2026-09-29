$ErrorActionPreference = 'Stop'
$outputDir = 'D:\Temp\combat-library-behavior-j75bzt8f\runs\baseline-L02'
$directReads = @(Get-Content -LiteralPath (Join-Path $outputDir 'input-evidence.json') -Raw -Encoding UTF8 | ConvertFrom-Json)
$internalReads = @(Get-Content -LiteralPath (Join-Path $outputDir 'script-input-evidence.json') -Raw -Encoding UTF8 | ConvertFrom-Json)
$commands = @(Get-Content -LiteralPath (Join-Path $outputDir 'commands-evidence.json') -Raw -Encoding UTF8 | ConvertFrom-Json)
$commands += [ordered]@{
    lookup = 5
    workdir = $outputDir
    exit_code = 0
    command = "& 'D:\Temp\combat-library-behavior-j75bzt8f\runs\baseline-L02\write_run.ps1'"
}
foreach ($commandRecord in $commands) {
    $commandRecord | Add-Member -NotePropertyName output_file -NotePropertyValue (Join-Path $outputDir ("lookup-{0}.txt" -f $commandRecord.lookup)) -Force
}
$run = [ordered]@{
    status = 'completed'
    request_path = Join-Path $outputDir 'request.txt'
    skill_root = 'D:\Temp\combat-library-behavior-j75bzt8f\baseline\skills\combat-director'
    answer_path = Join-Path $outputDir 'answer.md'
    input_files = @($directReads) + @($internalReads)
    read_mode_definitions = [ordered]@{
        full_direct_read = '完整内容通过命令输出直接阅读'
        partial_direct_read = '仅输出并阅读指定片段；本次无此类输入'
        hash_only = '仅计算哈希，未阅读内容；本次无此类独立输入'
        script_internal_read = '运行检索脚本时由 Python 审计 open 事件记录的冻结包文件读取；不代表直接完整阅读'
    }
    commands = $commands
    non_shell_operations = @(
        '使用 apply_patch 写入 answer.md 和 commands-evidence.json',
        '使用 apply_patch 写入本地 write_run.ps1'
    )
    evidence_notes = @(
        '所有输入范围限于指定请求和冻结技能包；自有可变产物未登记为输入。',
        '检索脚本通过输出目录内 trace_library.py 以 python -B 执行。',
        'catalog.json 的解析是脚本内部读取；模型只看到了 search 返回的一张候选。',
        '未读取主仓库、其他快照、评估资料或记忆，未联网、生成媒体、调用平台或启动其他代理。',
        '只依据柔道卡原文整理小内返，具体动作说明缺项。'
    )
}
$runPath = Join-Path $outputDir 'run.json'
$run | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $runPath -Encoding UTF8
$parsedRun = Get-Content -LiteralPath $runPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not (Test-Path -LiteralPath (Join-Path $outputDir 'answer.md'))) { throw 'Missing answer.md' }
foreach ($record in $parsedRun.input_files) {
    if ($record.sha256 -notmatch '^[a-f0-9]{64}$') { throw "Invalid SHA-256: $($record.path)" }
}
$summary = @(
    "status: completed"
    "answer: $(Join-Path $outputDir 'answer.md')"
    "run: $runPath"
    "direct input count: $($directReads.Count)"
    "script internal input count: $($internalReads.Count)"
    "input records:"
    ($parsedRun.input_files | ConvertTo-Json -Depth 8)
)
$summary | Set-Content -LiteralPath (Join-Path $outputDir 'lookup-5.txt') -Encoding UTF8
$summary
exit 0

