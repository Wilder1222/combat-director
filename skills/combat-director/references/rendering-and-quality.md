# 渲染路线、画质诊断与交付

仅在用户需要实际渲染方案、输出规格、引擎配置对齐或复杂画质诊断时读取。普通战斗提示词按[风格与材质](style-and-materials.md)写可见目标；本页不要求安装引擎，也不把尚未执行的方案写成已采用设置。

## 观感、制作与交付三层

| 层次 | 应明确的内容 | 不能由这一层证明的事 |
| --- | --- | --- |
| 画面观感 | 媒介与造型、皮肤/衣料/金属的响应、主光与空间层次、动态清晰和艺术处理 | 写UE、Path Tracing、ACES或8K不证明实际引擎、色彩流程或输出尺寸 |
| 资产与渲染路线 | 已有场景与角色资产、材质/毛发表示、所选渲染路径、摄影和时域处理的支持范围 | 高精度贴图不等于高分辨率成片，编辑器预览不等于最终帧序列 |
| 文件与显示交付 | 像素尺寸、画幅/裁切、帧率/净时长、文件格式/编码、色彩转换与目标显示 | 编码合规不证明动作、材质或光照好；升分辨率不自动修复模糊、闪烁和身份变化 |

先按用户已有入口决定能落实哪层。只有通用生成模型时，保留引擎名作为选定质感参考，并写可观察结果；已有三维制作入口时，另外给与本场资产相容的实施方案。普通正文不夹入控制台命令、样本数或编码字段；用户明确需要技术方案时另列。

## 按场景选择渲染路线

Lumen与Path Tracer属于不同计算路线，不把二者并列为同一镜头同时启用的画质套餐；动态全局照明、反射、材质与最终输出分别核对。

| 本次条件 | 路线与判断 |
| --- | --- |
| 已有UE实时场景，需交互预览、动态光与场景反馈 | 可评估Lumen的间接光与反射。微小且极亮的发光面可能产生噪声，全局光改变存在缓存更新过程；剑光可见、环境受照和光照更新各自检查 |
| 已有UE场景，需离线高质量帧序列 | 可评估Path Tracer与Movie Render Queue/Graph。先核实际版本、平台和硬件、材质/发丝/粒子/体积及动态模糊支持，再决定采样与降噪；不因路径追踪就改静止镜头 |
| 使用Unity HDRP或其他渲染器 | 按所选渲染路径核材质与摄影支持。同一透明、毛发或散射材质转到路径追踪时外观可能改变，不能复制UE配置或凭HDRP名称宣布同样结果 |

Path Tracer的编辑器视口累积与动画逐帧输出分开：视口中的移动或动态效果可能重启累积或形成拖痕，不能据此断言最终动画不支持；需要核最终渲染流程。同样，实时预览正常也不证明离线路径中所有效果、透明层和毛发已经相容。

## 材质与资产按风格选择

- **PBR与美术**：物理材质也可服务风格化三维。先保持原人物造型，再确定反射、粗糙度与色阶如何配合美术；赛璐璐、版画或水墨不默认改成写实皮纹。
- **皮肤**：分别选择底色/肤色变化、局部高光粗糙度、散射和微细节。真人近景可保留自然纹理与表情变化；风格化可概括微法线和斑点，仍保留面部体积与表情。SSS控制透光与散射，不用统一磨皮或全脸油亮代表高质量；薄部透光也不成为整身自发光。
- **头发**：按所需轮廓、镜头距离与实际支持选择发丝、发卡或概括发束。“独立发丝清晰”是观感目标，不能证明已有Groom资产或模拟；转身、逆光和擦镜时核轮廓、束间层次、动态与时域稳定。
- **布料与兵器**：薄纱透光、厚布挤皱、金线闪亮和金属刃面反射分别落实到实际对象；湿痕、粗糙度变化与磨痕可按剧情使用。皮肤、布料和金属不共用一种亮度/光泽；材质升级不自动更换服饰、兵器或新增破损。

需要真实资产方案时再核贴图、几何、LOD与材质质量等级。MetaHuman等数字人技术可以用于写实或风格化角色，不默认替换用户身份；某资产“8K贴图”或“电影级LOD”也不证明本次镜头采用了它，更不等于8K视频。

## 摄影与时域画质

相机位置/朝向、镜头视场、焦点/景深、曝光和动态模糊分别处理。朝向追踪不等于焦点追踪，视场由焦距与有效画幅共同决定，透视来自实际观察位置；浅景深还依赖对焦距离、光圈等条件。选定数值要能覆盖本次双方持手和接点。引擎中景深与物理曝光的关联由实际模式决定，不只凭摄影参数名推算。路线与焦点交接见[摄影](camera-and-rhythm.md)。

动态质量还包括时间上的稳定：原速和相邻帧检查发丝、剑缘、纱网、锦缎细纹、尘雾与高光是否闪烁、拖影、重影或被降噪抹去。特意的颗粒、飞白、残影与偶体姿态间距依所选美术判断；技术噪声不自动解释成艺术风格。

实际渲染中的空间采样、时间采样、抗锯齿、降噪、动态模糊与输出帧率各有职责。提高采样可改善某些边缘和噪声，也可能改变运动呈现；过多时间采样涉及场景求值与时间步限制。输出60fps不证明短曝光、慢镜或接触更清楚，4K/8K也不自动修复时域问题。

有布料、发丝或粒子模拟时，检查最终输出的开头状态与跨镜延续；实际渲染可需预热/历史建立，不给所有项目固定帧数。高分辨率分块还须核时域与屏幕空间效果兼容性，不能认为放大或分块总是无损保留原摄影。

## 光照、曝光与色彩交付

区分发光物的可见亮度、对皮肤/衣料/环境的照明，以及镜头或后期Bloom。飞剑可以轮廓明亮而附近受照有限；需要照亮地面时写来源、对象和变化。材质自发光、辅助光和画面光晕共同使用时核是否重复计光，不能让光晕吞掉刃形与握点。

确定稳定曝光还是有意适应明暗的曝光变化。普通剑光闪烁不自动让全场曝光来回抽动；用户选定耀光、压暗或过曝重音时按事件相位保留并恢复。Filmic/ACES式高光响应并不保证任意强度发光仍保有颜色，高亮可能趋白；“白衣层次”“双色剑光区分”应作为实际观察目标。

色彩分为场景线性数据、创意调色/色调映射、面向显示的转换与最终文件。ACES观感、OCIO配置、HDR显示输出和HDR文件各自核对：只写ACES HDR不证明已采用完整流程，也不保证用户显示器正在播放HDR。按实际交付选SDR或HDR、目标色彩空间/转换、编码与必要元数据，避免重复套显示转换。

用于后期的EXR可保留高动态线性数据；启用色调曲线与禁用曲线的EXR结果不同，常见8位图片及视频也不能按EXR流程描述。色彩、编码、尺寸和帧率通过后，仍需在目标显示条件检查暗部、亮部、皮肤、服饰、剑光与动态；没有实际文件和观看证据时，只报告计划或文字目标。

## 一手依据与适用边界

核对日期2026-10-10。Epic本次默认正文标为UE5.8；Unity比较读取HDRP17.3及Unity6.3 LTS页面。它们是文档快照，不是用户已安装版本；具体入口明确后重新核相应版本与模式。本次只读文字，未运行引擎、渲染或验证本项目媒体。

- [Epic物理材质](https://dev.epicgames.com/documentation/en-us/unreal-engine/physically-based-materials-in-unreal-engine)、[MetaHuman风格化材质](https://dev.epicgames.com/documentation/metahuman/metahuman-stylized-character-texture-and-material-editing)：PBR可用于非写实，皮肤细节与材质响应按美术校准。
- [MetaHuman材质与纹理](https://dev.epicgames.com/documentation/metahuman/metahuman-materials-and-textures)、[Groom表示](https://dev.epicgames.com/documentation/unreal-engine/hair-rendering-and-simulation-in-unreal-engine)：贴图、LOD、材质等级及发丝/发卡属于真实资产条件，不由文本保证。
- [Lumen](https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine)、[Path Tracer](https://dev.epicgames.com/documentation/en-us/unreal-engine/path-tracer-in-unreal-engine)：实时光照与离线输出、动态累积与特性支持分别核；当前发丝等支持仍有实验或部分支持边界。
- [Cine Camera](https://dev.epicgames.com/documentation/en-us/unreal-engine/cinematic-cameras-in-unreal-engine)、[MRQ图像设置](https://dev.epicgames.com/documentation/en-us/unreal-engine/cinematic-rendering-image-quality-settings-in-unreal-engine)：相机追踪、焦点、时空采样、预热和颜色输出各有控制范围。
- [渲染输出格式](https://dev.epicgames.com/documentation/en-us/unreal-engine/cinematic-render-settings-and-formats-in-unreal-engine)、[Filmic色调映射](https://dev.epicgames.com/documentation/en-us/unreal-engine/color-grading-and-the-filmic-tonemapper-in-unreal-engine)、[HDR显示输出](https://dev.epicgames.com/documentation/en-us/unreal-engine/high-dynamic-range-display-output-in-unreal-engine)：EXR线性数据、色调曲线和目标显示区别，不能把ACES等同所有HDR交付。
- [Unity HDRP路径追踪](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.3/manual/path-tracing-understand.html)、[SSS与透射](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.3/manual/skin-and-diffusive-surfaces-subsurface-scattering.html)、[动态模糊](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.3/manual/Post-Processing-Motion-Blur.html)、[HDR输出](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.3/manual/HDR-Output.html)：用于对照相同观感在另一渲染路线中的条件，不互套UE实现。
