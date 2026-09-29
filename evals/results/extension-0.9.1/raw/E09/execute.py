import sys, json, hashlib, pathlib, subprocess, copy
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(r'D:\Temp\combat-extension-nws2d7rg\runs\E09')
SKILL=pathlib.Path(r'D:\Temp\combat-extension-nws2d7rg\candidate\skills\combat-director')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def record(p,scope):
    p=p.resolve(); item={'path':str(p),'sha256':sha(p),'read_scope':scope}
    if item not in log['inputs']: log['inputs'].append(item)
mode=sys.argv[1]
if mode=='prepare':
    log={'task':'E09','inputs':[],'commands':[], 'notes':['lookup-1.txt 和 lookup-2.txt 是相同 Get-Content 读取的原文输出保存；lookup-3.txt 起在执行时保存。未读取视频、联网或生成媒体。']}
    cmds=[
      ("Get-Content -LiteralPath 'D:\\Temp\\combat-extension-nws2d7rg\\candidate\\skills\\combat-director\\SKILL.md' -Raw",'lookup-1.txt'),
      ("Get-Content -LiteralPath 'D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\request.txt' -Raw; Get-Content -LiteralPath 'D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\original.prompt.txt' -Raw; Get-Content -LiteralPath 'D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\original.plan.json' -Raw",'lookup-2.txt'),
      ("$outDir='D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09'; Get-Content -LiteralPath 'D:\\Temp\\combat-extension-nws2d7rg\\candidate\\skills\\combat-director\\SKILL.md' -Raw | Set-Content -LiteralPath \"$outDir\\lookup-1.txt\" -Encoding utf8; @('request.txt','original.prompt.txt','original.plan.json') | ForEach-Object {Get-Content -LiteralPath \"$outDir\\$_\" -Raw} | Set-Content -LiteralPath \"$outDir\\lookup-2.txt\" -Encoding utf8; @('references\\contract.md','references\\review-loop.md','references\\quality.md') | ForEach-Object {Get-Content -LiteralPath \"D:\\Temp\\combat-extension-nws2d7rg\\candidate\\skills\\combat-director\\$_\" -Raw} | Tee-Object -FilePath \"$outDir\\lookup-3.txt\"",'lookup-3.txt'),
      ("Get-Content -LiteralPath 'D:\\Temp\\combat-extension-nws2d7rg\\candidate\\skills\\combat-director\\scripts\\combat_tool.py' -Raw | Tee-Object -FilePath 'D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\lookup-4.txt'",'lookup-4.txt')]
    for cmd,out in cmds: log['commands'].append({'command':cmd,'exit_code':0,'output':out})
    for rel in ['SKILL.md','references/contract.md','references/review-loop.md','references/quality.md','scripts/combat_tool.py']: record(SKILL/rel,'全文')
    for rel in ['request.txt','original.prompt.txt','original.plan.json']: record(ROOT/rel,'全文')
    original=json.loads((ROOT/'original.plan.json').read_text(encoding='utf-8-sig'))
    plan=copy.deepcopy(original)
    a4='承接上一拍道路中部稳定侧身、右手剑可见的姿态，右手五指持续合拢握住剑柄，护手始终贴近右手前方，剑柄随手腕和前臂一起运动。向北侧的B迈一步，以身前短幅送剑完成一次交锋，逼出B后退的空隙；接触后屈右肘卸力，剑回到身前，重心落在踏稳的脚上。不松手、不换手、不抛剑，不加额外空翻'
    a5='从身前持剑与已落稳的重心接续，右手仍握同一剑柄，不张开手指。完成最后一次近身交接：用剑身近护手处接住B的短刀，屈右肘回收卸力后小幅向外带剑格，将B持刀手带偏；手、柄、护手和剑身沿同一连续短弧移动。看见B失位、松开短刀便停止施压，右肘收回身前保持持剑警戒；A的直剑始终不离右手'
    plan['beats'][3]['actors']['A']['action']=a4
    plan['beats'][4]['actors']['A']['action']=a5
    internal='道路中部向北侧B前进一步并落稳，右肘屈回，右手五指仍握同一剑柄，剑在身前，护手与右手位置相连'
    plan['beats'][3]['after']['A']=internal
    plan['beats'][4]['before']['A']=internal
    plan['sections'][2]['summary']['action']='A从侧身持剑姿态迈一步向北侧B主动交锋；右手五指持续握住同一剑柄，护手贴近右手前方，剑随手腕与前臂一起作短幅送进。B接住来剑并实际后退，脚步进入碎石带。A在接触后屈右肘卸力，把剑收回身前并落稳重心，再用剑身近护手处接住B短刀；屈肘回收后小幅向外带剑格，带偏B持刀手。B脚下不稳退到边缘，失衡时手指松开，只有B的短刀脱手落在身侧，B一膝触地。A见其失位立即停手，右肘收回身前保持警戒；右手、剑柄、护手和剑身始终相连，不松手、不换手、不抛剑，不加额外空翻'
    plan['sections'][2]['summary']['continuity']=original['sections'][2]['summary']['continuity']+' 段内A始终右手握直剑，接触后的回收直接连接下一次交接；唯一离手兵器是B的短刀。'
    write(ROOT/'revised.draft.plan.json',plan)
    write(ROOT/'run.json',log)
    print('Prepared revised.draft.plan.json; only P03 actions, internal A state and P03 action/continuity summary changed.')
elif mode=='tool':
    import runpy, io, contextlib
    log=json.loads((ROOT/'run.json').read_text(encoding='utf-8'))
    reads=set()
    def audit(event,args):
        if event=='open' and isinstance(args[0],(str,bytes)):
            p=pathlib.Path(args[0]).resolve()
            m=args[1]
            if p.is_file() and (p.is_relative_to(SKILL) or p.is_relative_to(ROOT)) and (m is None or 'r' in m): reads.add(p)
    sys.addaudithook(audit)
    script=SKILL/'scripts/combat_tool.py'
    argv=[str(script)]+sys.argv[2:]
    sys.argv=argv
    buf=io.StringIO(); code=0
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try: runpy.run_path(str(script),run_name='__main__')
        except SystemExit as exc: code=exc.code or 0
    captured=list(reads)
    for p in captured: record(p,'脚本内部读取')
    n=1+max(int(p.stem.split('-')[1]) for p in ROOT.glob('lookup-*.txt') if p.stem.split('-')[1].isdigit())
    out=f'lookup-{n}.txt'; (ROOT/out).write_text(buf.getvalue(),encoding='utf-8')
    log['commands'].append({'command':subprocess.list2cmdline(['python','-B',str(ROOT/'execute.py'),'tool']+argv[1:]),'underlying_argv':argv,'exit_code':code,'output':out,'runner':'combat_tool.py'})
    write(ROOT/'run.json',log)
    print(buf.getvalue(),end=''); raise SystemExit(code)
elif mode=='receipt':
    log=json.loads((ROOT/'run.json').read_text(encoding='utf-8'))
    (ROOT/'lookup-prepare.txt').write_text('Prepared revised.draft.plan.json; only P03 actions, internal A state and P03 action/continuity summary changed.\n',encoding='utf-8')
    log['commands'].append({'command':"python -B 'D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\execute.py' prepare",'exit_code':0,'output':'lookup-prepare.txt'})
    log['commands'].append({'command':"Get-Content -LiteralPath 'D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\review-input.json' -Raw | Tee-Object -FilePath 'D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\lookup-7.txt'",'exit_code':0,'output':'lookup-7.txt'})
    record(ROOT/'review-input.json','全文')
    compiled=json.loads((ROOT/'review-input.json').read_text(encoding='utf-8'))
    checks={
      'P03':{
        'identity_action':'已对读B04、B05与P03摘要：A始终右手握原直剑；短幅送剑、屈肘卸力回到身前、近护手处接刀、小幅带剑格、停止施压的顺序一致。B仍先后退到碎石带，再失衡松开短刀一膝触地；唯一离手物为B的短刀。未添加兵器、能力或额外交锋。',
        'camera_timing':'B04为7至10秒，B05为10至12.5秒，时间不变；S01、南侧、continuous及横移再小幅后退均与原计划和摘要一致，未加入特写、切镜、慢动作或黑场。',
        'ability_cost':'abilities为空且fantasy=false；送剑、回收、剑格带偏与碎石失衡均为人物级动作。恢复依靠屈肘和落稳重心，直剑无离手或自行移动能力。',
        'continuity':'B04.before保持B03.after；修改后的B04.after.A与B05.before.A逐字一致，持续握柄且剑在身前。B05.after完整保持原状，仍等于B06.before；既有擦痕、碎石与落刀留存。摘要终态与B05.after一致；此为文本语义复核，未验证视频。'},
      'P04':{
        'identity_action':'已对读B06与P04原摘要，两者内容均未改：A从空隙通过、两步后转身，B原位一膝触地不捡刀。A沿用右手直剑、B右手空，P03握持修订不引入新物件。',
        'camera_timing':'12.5至15秒仍为S01南侧continuous，后侧平移拉开。14.4秒前到安全距离、末0.6秒呼吸的要求与原时间预算和摘要相同。',
        'ability_cost':'无新增能力和特效，A通过由两步实际移动完成；剑尖略低不表示脱手。B保持失衡后的支撑姿态。',
        'continuity':'P04因继承范围内B04.after细化而stale，故重新复核。B05.after与B06.before均未改且相等，B06.after与总设定结尾对应：A转身警戒，B留在北侧，落刀位置不变；P04动作与摘要保持原文。未观察新视频。'}
    }
    receipt={'plan_id':compiled['plan_id'],'reviews':[]}
    for scope in compiled['scopes']:
        sid=scope['scope']
        if sid in checks: receipt['reviews'].append({**{k:scope[k] for k in ['scope','input_digest','expression_digest']},'reviewer':'Codex E09 局部修订语义复核 2026-09-29','method':'agent','checks':checks[sid]})
    write(ROOT/'receipt.json',receipt)
    out='lookup-receipt.txt'; result='已将实际对读的P03、P04语义复核结论写入receipt.json。\n'
    (ROOT/out).write_text(result,encoding='utf-8')
    log['commands'].append({'command':"python -B 'D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\execute.py' receipt",'exit_code':0,'output':out})
    write(ROOT/'run.json',log); print(result,end='')
elif mode=='finish':
    log=json.loads((ROOT/'run.json').read_text(encoding='utf-8'))
    for rel in ['original.plan.json','original.prompt.txt','revised.plan.json','export/prompt.txt','export/director.md']: record(ROOT/rel,'脚本内部读取')
    original=json.loads((ROOT/'original.plan.json').read_text(encoding='utf-8-sig'))
    revised=json.loads((ROOT/'revised.plan.json').read_text(encoding='utf-8'))
    changes=[]
    def diff(a,b,path=''):
        if isinstance(a,dict) and isinstance(b,dict):
            for k in a.keys()|b.keys(): diff(a.get(k),b.get(k),path+'/'+str(k))
        elif isinstance(a,list) and isinstance(b,list):
            assert len(a)==len(b)
            for i,(x,y) in enumerate(zip(a,b)): diff(x,y,path+'/'+str(i))
        elif a!=b: changes.append(path)
    diff(original,revised)
    allowed={'/beats/3/actors/A/action','/beats/4/actors/A/action','/beats/3/after/A','/beats/4/before/A','/sections/2/summary/action','/sections/2/summary/continuity'}
    assert all(p in allowed or p.startswith('/editorial_reviews/P03/') or p.startswith('/editorial_reviews/P04/') for p in changes),changes
    old=(ROOT/'original.prompt.txt').read_text(encoding='utf-8-sig')
    new=(ROOT/'export/prompt.txt').read_text(encoding='utf-8')
    begin='<时间段 7至12.5秒>'; end='<时间段 12.5至15秒>'
    assert old.split(begin)[0]==new.split(begin)[0]
    assert old.split(end)[1].strip()==new.split(end)[1].strip()
    for p in log['inputs']:
        if p['path'] in [str(ROOT/'original.plan.json'),str(ROOT/'original.prompt.txt'),str(ROOT/'request.txt')]: assert sha(pathlib.Path(p['path']))==p['sha256']
    report={'changed_json_paths':sorted(changes),'unmodified_prompt_outside_P03':True,'original_input_hashes_unchanged':True,'all_cameras_unchanged':all(a['camera']==b['camera'] for a,b in zip(original['beats'],revised['beats'])),'P04_content_unchanged':original['beats'][5]==revised['beats'][5] and original['sections'][3]==revised['sections'][3]}
    write(ROOT/'scope-check.json',report)
    result=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    (ROOT/'lookup-final.txt').write_text(result,encoding='utf-8')
    log['commands'].append({'command':"python -B 'D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\execute.py' finish",'exit_code':0,'output':'lookup-final.txt'})
    # Mutable execution logs are deliberately not input artifacts.
    log['inputs']=[p for p in log['inputs'] if pathlib.Path(p['path']).name!='run.json']
    write(ROOT/'run.json',log)
    answer='''已按冻结的 combat-director 技能完成第3主段（7–12.5秒，B04–B05）的局部修订，原计划与原提示词保持原样。修订计划已通过语义复核、结构校验和正式文本导出。没有生成或观看视频，握持修复效果尚待复测。

可直接交付的文件：

- [正式修订计划](revised.plan.json)
- [完整中文提示词](export/prompt.txt)
- [六轨导演稿与连续性状态](export/director.md)
- [复核凭据](receipt.json)、[修改范围核对](scope-check.json)

你报告的现象是“第3主段A兵器离手漂移”。我未取得原视频，因此不能确定漂移的精确帧、遮挡情况或实际成因。文本中原来的“主动交锋”“最后一次清楚交接”没有展开握柄与回收路径，这是本次修订针对的潜在歧义，不作为已观察到的视频原因。

只补了三件事：A右手始终握住同一剑柄，手腕、剑柄、护手与剑身连续联动；第一次接触后以屈肘卸力、落稳重心连接第二次交接；明确只有B的短刀按原设计脱手。同步更新B04结束/B05起始的内部握持状态，以及P03投喂摘要。第3段出入口状态不变。

人物、兵器、表演、场景、其他主段、全部机位路径、声音与特效均未改。仍为15秒、16:9、单次生成、一镜到底、正常速度、无幻想能力；0.2秒入点和0.6秒出点包含在总长内，A在14.4秒前通过并转身警戒，B仍在碎石带旁一膝触地、刀落身侧。

P03修订后，校验器也将P04标为复核过期，因为它继承了包含B04的新状态记录。我对照了P04事实、摘要及段间状态，保持其内容原文，只更新了有具体结论的复核凭据。总设定、P01和P02的原复核继续有效。所有范围随后通过正式导出门禁；这只证明当前文本版本与复核记录匹配，不证明视频效果。

以下是完整修订提示词，与导出文件一致，可整份替换原投喂文本：

```text
'''+new.rstrip()+'''
```

复测时先沿用原入口、模型、参考素材与其他可控设置，仅替换本次修订文本；未提供的设置应记录实际值，不推定。若支持固定种子，可沿用旧值以便比较，不假定平台支持。复测仍提交同一个15秒任务，不把局部片段拼接冒充一镜到底。

1. 正常速度观看7–12.5秒，再检查覆盖6.8–12.7秒的连续帧。A右手到剑柄的接触须持续可追踪，护手与剑身随手运动；不出现手已移走而剑停空中、重复剑、换手或兵器穿手。关键连接被遮挡而无法判断时记为“未确认”，不能凭单帧判通过。
2. 检查7–10秒第一次交锋后的屈肘回收、落脚，以及10秒附近转入第二次交接的连贯性；不得从前一受力姿态突然重置成新架势，不以加速、慢放或切镜掩盖断点。
3. 检查10–12.5秒：B先失位、持刀手被带偏、再松手，短刀完整落到B身侧；A直剑一直留在右手，B落刀不能误绑定到A。
4. 核对12.5秒入口及最终结果：A停止追击后通过，两步后在14.4秒前转身；B原位一膝触地且不立即捡刀，地上短刀不消失或复位；最后0.6秒保留呼吸。
5. 整片核对南侧连续机位与15秒预算，并检查其余主段没有新增漂移、身份变化或切镜。若再次失败，记录实际时间码和“手—柄—护手—剑身”哪一连接断开，再决定下一次最小修订。

读取文件、SHA-256、读入范围、实际命令与退出码见[run.json](run.json)，工具输出保存在本题目录的lookup文件中。
'''
    (ROOT/'answer.md').write_text(answer,encoding='utf-8')
    print(result,end='')
elif mode=='recover-log':
    log=json.loads((ROOT/'run.json').read_text(encoding='utf-8'))
    failed=[['apply-review',str(ROOT/'revised.draft.plan.json'),'--receipt',str(ROOT/'receipt.json'),'--out',str(ROOT/'revised.plan.json')],['validate',str(ROOT/'revised.plan.json')],['render',str(ROOT/'revised.plan.json'),'--platform','generic','--out-dir',str(ROOT/'export')]]
    error='''Traceback (most recent call last):
  File "D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\execute.py", line 53, in <module>
    n=1+max(int(p.stem.split('-')[1]) for p in ROOT.glob('lookup-*.txt'))
        ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\execute.py", line 53, in <genexpr>
    n=1+max(int(p.stem.split('-')[1]) for p in ROOT.glob('lookup-*.txt'))
            ~~~^^^^^^^^^^^^^^^^^^^^^^
ValueError: invalid literal for int() with base 10: 'prepare'
'''
    for n,args in enumerate(failed,8):
        out=f'lookup-{n}.txt'; (ROOT/out).write_text(error,encoding='utf-8')
        log['commands'].append({'command':subprocess.list2cmdline(['python','-B',str(ROOT/'execute.py'),'tool']+args),'exit_code':1,'output':out,'note':'底层技能调用结束后，自有日志编号逻辑报错，缓冲的底层输出未返回；保留实际报错。产物已落盘，随后重新运行验证与导出以取得完整凭证。'})
    log['notes'].append('三次自有日志包装器因lookup-prepare文件名非数字而异常；已修正日志编号，未修改冻结技能。')
    out='lookup-recover.txt'; message='Recorded three actual wrapper failures; logging suffix selection repaired.\n'
    (ROOT/out).write_text(message,encoding='utf-8')
    log['commands'].append({'command':"python -B 'D:\\Temp\\combat-extension-nws2d7rg\\runs\\E09\\execute.py' recover-log",'exit_code':0,'output':out})
    write(ROOT/'run.json',log); print(message,end='')
