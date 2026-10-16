# CLEAR 會議總整理 — The Missing Layer

**給 Cyrus:**這份文件是 10 月 15 日晚間到 16 日凌晨所有討論、研究和設計決定的總集合。會前讀第 0、1、13 節就夠;細節在後面備查。

**日期:** 2026-10-16(星期五,今天)
**對象:** CLEAR(已回信同意會面)
**目標:** 招募合作者,不是推銷產品。要三樣東西:一門試點課程、認識 Dr. Pang 和 Prof. Hargreaves 的引薦、Teaching and Learning Innovation Expo 2026(12 月 14–15 日)學生海報的資訊。

---

## 0. 今天要做什麼(30 秒版)

1. 帶 v0.1 原型(`proof-of-understanding-v0.1.html`,離線單一 HTML,直接打開)。
2. 開場:**"Since I wrote to you, I tried to break my own design. It broke. What I'd like to show you is what survived."**
3. 講一個概念:**反轉**——"Students today get the answer first and ask for the explanation later. We reverse it."
4. 問一個問題:**"If every AIAS level could compile into a pipeline that runs, which course would you pilot first?"**
5. 提出三個請求(試點課、Pang、Hargreaves、Expo 海報)。
6. 紀律:不做 pitch deck、"platform" 最多講一次、不談商業。

你已有的材料**足夠**應付第一次會議。第一次會議的目標是找合作者,不是展示完整方案。

---

## 1. 核心論點(一句話)

> **"We don't police the output. We gate the input. Understanding is the key to the evidence."**

學生先要理解,才問得出能解鎖答案的問題。**問題本身就是理解的證據。**

英文完整版:
> *"Students today get the answer first and ask for the explanation later. We reverse it: you have to understand first — because only an understanding question unlocks the answer."*

---

## 2. 為什麼「給多少 AI」是錯的問題

- 所有校控 AI(包括我們之前的設計)都在管「**用多少**」,沒有設計「**用在哪個位置**」。
- Lee 2026 的概念模型:LLM 對學習有三種作用——**繞過(bypass)、卸載(offload)、搭鷹架(scaffold)**。
- Bastani et al. 的實驗:同一個 GPT-4,兩種設計,結果相反。普通版練習時 +48%,拿走 AI 後 **−17%**;有學習保護的 Tutor 版練習時 +127%,拿走後傷害大致消除。**決定結果的不是 AI 的量,是 AI 扮演什麼角色。**
- 結論:**AI 可以是環境,但永遠不是作者(the author)。答案只能從學生身上出來。**

---

## 3. 那個讀書的學生(reel 基準):他做了四件事

他不是靠「沒有 AI」學會的。書不會直接回答他,他被迫做了四件 AI 平常替學生做掉的事:

| 他做的事 | 為什麼有效 | 研究依據 |
|---|---|---|
| 先自己想,卡住 | 失敗的提取嘗試促進之後的學習;先解題再受教 | Kornell, Hays & Bjork 2009;Kapur「productive failure」 |
| 把書的話翻譯成題目需要的話 | 會讓人慢下來的困難,讓理解留得住 | Bjork「desirable difficulties」 |
| 消化成自己的話 | 壓縮就是理解;自己生成的記得更牢 | 生成效應(generation effect) |
| 憑腦袋作答 | 答案從他自己身上出來 | 正是 Bastani「拿走 AI 之後」那一刻 |

**書的摩擦力是功能,不是缺點。** 關鍵變數不是 AI 存取量,而是**誰執行認知轉換**。

---

## 4. 大反轉(你自己說的,整個方案的心臟)

> **一般情況:先拿答案,再問為什麼。我們反過來:先理解,才問得出能拿到答案的問題。**

- 外部 AI 不能代替學生問,因為**問題就是理解的證據**——不懂的人連該問什麼都不知道。
- 教學生自己生成問題,理解測驗效應量中位數 **0.86**(實驗者自編測驗)、0.36(標準化測驗)。Rosenshine, Meister & Chapman 1996。
- 學生問題的類型反映思考深度:基本資訊題=淺層學習,深層問題=深層學習。Chin 2001;Chin & Osborne 2008。
- **誠實但書:** Person & Graesser 1994 發現問題品質只是理解的「邊際指標」,學生的**回答**才最可靠。所以問題記錄必須搭配 v0.1 的房間檢查(Room)——v0.1 沒有白做。

---

## 5. 三個機制(所有任務設計的積木)

| 機制 | 意思 | 為什麼外部 AI 幫不上全部 |
|---|---|---|
| **Hidden 隱藏** | 解題需要的資訊存在系統裡,一開始不給 | ChatGPT 看不到它 |
| **Budget 預算** | 只能查有限次數,每次要選擇查什麼 | 選擇查什麼,本身就是理解 |
| **Commit 先承諾** | 揭曉之前必須先鎖定預測或答案 | 已鎖定的答案不能事後改 |

研究根據:PISA 2012 把題目分成「靜態(全部資訊一開始給齊)」和「**互動(學生必須自己挖出部分資訊)**」,並當成獨立能力測量。德國 MicroDYN:規則被隱藏的線性系統,學生自己做實驗找出變數關係(Greiff & Funke;Schoppek et al. 2015)。

---

## 6. 引擎式任務:黑盒矩陣(線性代數 / Strang)

直接用已經挖好的 Strang 第一講板書時間點。

- **任務:** 系統藏一個 3×3 矩陣 A。學生可輸入任何向量 x,系統回傳 Ax。最多查 4 次。問題:存在 x 使 Ax = b 嗎?存在就找出來。
- **懂的學生**輸入 (1,0,0)、(0,1,0)、(0,0,1),三次拿到 A 的三個列——正是 Strang 18:27–27:57 講的「Ax 是列的線性組合」。
- **進階:** 藏奇異矩陣,b 不在列空間裡,學生要答「不存在,因為…」。
- **每次查詢前先預測輸出(Commit)。** 預測準確度顯示腦中的模型有沒有成形。
- **收據記錄的不是對錯,是查詢路徑:** 第幾次問對、預測多準、最後的解釋。

**繞過分析:** 學生問 ChatGPT「最少要查幾次?」它答「輸入三個單位向量」——但這就是那一講的核心概念,**他為了作弊被迫先學會了**。逐步轉貼也可以,但矩陣隨機,要來回十幾次還得自己判斷。

標準出自 Winstone et al. 2026(Black Box Assessment):設計不必防 AI,而是讓外包**「比真正參與更難、更冒險、更費力」**(harder, riskier, and more effortful than genuine engagement)。

---

## 7. 論文式任務:封存檔案庫(Sealed Archive)

寫論文的「答案」其實是**證據**。把證據封存,只有問得精準才拿得到。

**教授要做的事(不用寫 prompt):**
1. 上傳 20–40 份材料:講義、指定讀物、案例文件、數據。
2. 標記 1–2 份**轉折文件(hinge document)**:會推翻表面結論、只有懂核心張力的人才會想到要找的材料。**必須是課程專屬的**(教授講義、特定注疏、自編案例、私有數據)——公開材料 ChatGPT 都知道。
3. 設檢索預算(例如 12 次)。

**系統內 AI(圖書館員)四條規則:**
- 只回答指明具體主張/概念/文件的問題;太寬就退回:「範圍太大,你在驗證哪個主張?」
- 只回傳**原文段落和出處**,從不摘要、從不下結論。
- 每次檢索都記錄。
- 論文引用必須連結到實際檢索過的段落。

**例子(法律備忘錄:「房東能否終止租約?」):**

| 學生問 | 圖書館員回應 | 說明 |
|---|---|---|
| 「租約怎麼說?」 | 範圍太大。你在驗證哪個主張? | 不懂的人只能這樣問 |
| 「租約有沒有終止條款?」 | 回傳第 14 條原文 | 基本資訊題 |
| 「遲交租金之後,房東有沒有繼續收租?」 | 回傳 3、4 月收據 | **只有懂「棄權」(waiver)的人才會問——這就是轉折文件** |

**三個收據點:** 第一次檢索時的論點 vs 最終論點(論點有沒有隨證據演變);問題類型分布(找事實/驗證主張/找反證);轉折文件有沒有找到、第幾次。

**學科對照:**

| 學科 | 封存的是什麼 | 轉折文件 |
|---|---|---|
| 法律 | 案件卷宗 | 房東繼續收租的收據 |
| 歷史/政策 | 檔案文件 | 與官方說法矛盾的內部備忘錄 |
| 經典閱讀(Pang) | 特定版本注疏+教授講義 | 和主流讀法相反的注疏 |
| 商科 | 公司內部數據 | 讓成長故事破產的一個數字 |

**仍然擋不住的:** 學生把檢索到的段落貼給 ChatGPT 寫成論文。但外部 AI 只拿得到學生自己問出來的東西——**論文品質的上限=問題品質的上限**,沒問出轉折文件的人,論點一定漏掉案件核心,教授一眼看得出。

---

## 8. AI 的五個位置(較早的框架,會上可用但別當主角)

| 位置 | 運作 | 學生被迫做什麼 |
|---|---|---|
| 圖書館 | 只指出位置,不給綜合答案 | 自己讀、自己翻譯 |
| 學生(教 AI) | AI 只知道你告訴它的 | 用自己的話講清楚(protégé effect;Betty's Brain) |
| 對手 | AI 有說服力地論證錯誤答案 | 找錯並反駁(正是 Hargreaves 的 "improve upon an AI answer") |
| 鏡子 | 只用學生自己的話指出推理空隙 | 看見自己哪裡沒想通(Pang 的 Mirror) |
| 考官 | 打字房間 | 證明理解發生過 |

共同點:**答案只能從學生身上出來。**
**已否決:** 角色扮演(陳太太)——太遠,不用。
**注意:** 這五個位置在家裡做全都可以繞過,所以需要第 5 節的三個機制配合。

---

## 9. 教授沙盒(模組化)

教授不寫 prompt,只填一張表:

| 欄位 | Strang(線代) | Hargreaves(法律) | Pang(經典閱讀) |
|---|---|---|---|
| 隱藏的是什麼 | 矩陣 A | 30 份案件文件 | 文本上下文和注疏 |
| 預算 | 4 次查詢 | 開 5 份 | 查 6 個注疏 |
| 先承諾什麼 | 查詢前預測輸出 | 開文件前先寫目前判斷 | 先寫自己的詮釋再看注疏 |
| 職場對應 | 工程師除錯 | 律師證據開示(discovery) | 研究者查證 |

**和 AIAS 的橋接(CLEAR 已辦過 AIAS 工作坊,Perkins 2025 年 7 月):**
> *"You teach professors AIAS in workshops. This compiles each AIAS level into a pipeline that runs."*

AIAS 每一級都可以編譯成一條積木路徑。原本老師只能「告訴」學生這份作業是 Level 2(話語式改革,Corbin 說的 enforcement illusion);現在等級**就是**作業本身的流程(結構式改革)。

**AIAS 是什麼(備查):** AI Assessment Scale,Perkins/Roe/Furze/MacVaugh 2023 年首發,現為 2.1 版,350+ 院校、30+ 語言。五級:No AI / AI Planning / AI Collaboration / Full AI / AI Exploration。本質是一張**標籤**,第 2–5 級靠學生自覺——Sydney 大學因此放棄中間級別(two-lane)。已整合進 Studiosity Validate(在 LMS 選級別+作者身份驗證),所以「AIAS+驗證」已有人做,**不要說成沒人做過**。

---

## 10. 誠實邊界(會上被問到就照這樣答)

1. **沒有 100% 防作弊。** 標準是 Winstone 2026:讓外包比真正參與更難、更冒險、更費力。
2. **公開材料的部分是漏洞。** 《孟子》原文 ChatGPT 全知道。轉折文件必須課程專屬——這是教授的設計成本。
3. **問題品質不能單獨當判斷依據**(Person & Graesser 1994),要搭配房間檢查。
4. **寫作這一步仍可外包**(封存檔案庫擋的是材料取得,不是成文)。
5. **抗 AI 程度是我們的判斷,不是研究結論。** 引用的研究證明的是學習效果,沒測過抗 AI。這正是試點要驗證的。
6. **類似想法存在:** 醫學 virtual patient、法律模擬客戶,LLM 版也開始出現。安全講法:**把這種模擬變成任何教授都能用的通用積木,並取代傳統帶回家作業**。
7. **摩擦會趕跑學生。** 收據必須在成績或作品集裡算數——決定權在教授。
8. **校外仍然管不到。** 不抓人,只是那種做法拿不到收據。

---

## 11. 研究武器庫(全部已核實來源)

### 學習科學
- **Bastani et al.**(SSRN 4895486):GPT Base +48% / GPT Tutor +127% 練習;拿走後 −17%;Tutor 保護大致抵銷傷害。https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4895486
- **Rosenshine, Meister & Chapman 1996**:教學生生成問題,效應量中位數 0.36(標準化測驗)/ 0.86(自編測驗)。https://journals.sagepub.com/doi/10.3102/00346543066002181
- **Chin 2001**(學生問題反映思考深度):https://repository.nie.edu.sg/bitstreams/cfa6e8c3-4dca-45ec-92f2-790e4763cdf1/download
- **Chin & Osborne 2008**(學生問題是學習資源):https://www.tandfonline.com/doi/full/10.1080/03057260701828101
- **Person & Graesser 1994**(問題品質只是邊際指標——誠實但書):https://www.sciencedirect.com/science/article/pii/1041608094900108
- **Schwartz & Bransford 1998 "A Time for Telling"**(對比案例、先發明後受教):https://aaalab.stanford.edu/papers/time_for_telling.pdf
- **McLaren 2015**(找錯:即時測驗無差別,**延遲測驗顯著更好**):https://link.springer.com/article/10.1007/s40593-015-0064-x ;Richey 2019(困惑越多學越好):https://www.learntechlib.org/p/209945
- **POE(White & Gunstone)**:先預測再揭曉。https://arbs.nzcer.org.nz/predict-observe-explain-poe
- **Kornell, Hays & Bjork 2009**(失敗的提取嘗試促進學習):https://psycnet.apa.org/record/2009-09620-017
- **Kapur productive failure、Bjork desirable difficulties、生成效應**(教科書級,口頭引用即可)

### 測驗設計(隱藏資訊)
- **PISA in Focus N38**(互動題:學生必須自己挖資訊):https://www.meb.gov.tr/earged/oecd/PISA%20in%20Focus%20N38%20(eng)--Final%20bis.pdf
- **MicroDYN**(Greiff & Funke;Schoppek et al. 2015):https://pmc.ncbi.nlm.nih.gov/articles/PMC4633517/
- **Unfolding case studies**(護理,Cheng 2024):https://www.sciencedirect.com/science/article/pii/S0260691724000789

### 評估改革(AI 時代)
- **Winstone et al. 2026 "Black Box Assessment"**(結構式回應;過程證據「windows」;錯誤是學習證據;外包門檻標準):https://www.tandfonline.com/doi/full/10.1080/02602938.2026.2661365
- **Corbin et al. 2025**(discursive vs structural;wicked problem;enforcement illusion):https://www.tandfonline.com/doi/full/10.1080/02602938.2025.2503964
- **Nikolić 2026**(四支柱:過程記錄、口試防衛、真實任務、透明 AI 政策):https://pmc.ncbi.nlm.nih.gov/articles/PMC13422401/
- **Perkins 2026**(resilient assessment,真實任務):https://www.tandfonline.com/doi/full/10.1080/02602938.2026.2644516
- **OECD Digital Education Outlook 2026**:把任務外包給 GenAI「只是提升表現,沒有真正學習增益」。https://www.oecd.org/en/publications/oecd-digital-education-outlook-2026_062a7394-en.html
- **Lee 2026**(bypass / offload / scaffold):https://osf.io/preprints/edarxiv/8f376
- **UNESCO 2025**:現有量測只靠自我報告。

### 幻覺 of understanding 證據
- **Fan et al. 2025**(BJET,"metacognitive laziness"):https://research.monash.edu/en/publications/beware-of-metacognitive-laziness-effects-of-generative-artificial/
- **Kosmyna et al.**(MIT Media Lab EEG,LLM 使用者「難以引用自己的作品」;preprint,n=54):https://www.media.mit.edu/publications/your-brain-on-chatgpt/
- **Kizilates et al.**(SSRN 7574738,"illusion of competence")

### 市場(誰做了什麼——定位時用)
- GPTZero Writing Replay;**Grammarly Authorship**(2024 年 8 月,用了 "receipts" 這個詞);**Turnitin Clarity**(2025 年 7 月,UCLA、Fresno State;有監控反彈)。
- **ChatGPT Edu、Gemini for Education**——校控 AI 已存在,我們不與之競爭。
- **Perusall Confusion Report**(靠學生自我標記);Khanmigo Teacher Reports(建基於學生自己的 chat)。
- 語音 AI viva($15 / 36 場考試,arXiv 2603.18221);Davalos & Zhang(arXiv 2609.17883);DraftTrace(arXiv 2609.36544)。
- **AIAS**:https://aiassessmentscale.com/ (350+ 院校;Studiosity Validate 整合;AIAS Advisor GPT)。
- **Sydney two-lane FAQ**(放棄中間級別):https://educational-innovation.sydney.edu.au/teaching@sydney/frequently-asked-questions-about-the-two-lane-approach-to-assessment-in-the-age-of-ai/

### 定位句(對比競品時用)
- "Clarity points the meter at the student. We point it at the learning."
- "Authorship proves who wrote it. Ours proves you understood it."
- "Perusall shows you what students know they don't understand. We show you what they think they understand — but don't. On your own lecture timeline."

---

## 12. 設計定律(節選自 ultimate-proposal-v2 §4,共 11 條,今晚新增兩條在最前)

1. **先理解,才問得出問題**(大反轉)。
2. **我們不抓出口,我們鎖入口**(gate the input, not police the output)。
3. 幫你思考,永不替你思考。
4. AI 觸碰結構,永不觸碰內容。
5. 永遠不是作弊報告。
6. 教授被放大,不被取代。
7. 校外研究不受監督;房間裡才賺得到證明。
8. 永不與 NotebookLM、ChatGPT Edu、Gemini Edu 競爭。
9. 核心機制:理解必須在任何東西送出去之前發生一次。
10. 偽造過程本身就是學習。
11. 沒有 100% 防作弊宣稱。

---

## 13. 今天的會議劇本

**帶什麼:** v0.1 原型(離線 HTML)+ 這份文件第 1、5、7 節的對照表(可口述)。如果黑盒矩陣 demo 做好了,加它。

**開場:**
> "Since I wrote to you, I tried to break my own design. It broke. What I'd like to show you is what survived."

**主軸(三分鐘版):**
1. 帶回家作業失效,因為作業把 ChatGPT 需要的一切都給了它。
2. 反轉:答案不再免費——理解是取得材料的鑰匙,問題本身就是理解的證據。
3. 現場開 v0.1,讓對方親自體驗一次。

**要問的問題:**
- "If every AIAS level could compile into a pipeline that runs, which course would you pilot first?"
- 能否引薦 Dr. Pang 和 Prof. Hargreaves。
- CLEAR Teaching and Learning Innovation Expo 2026(12 月 14–15 日)的徵稿——學生合作海報。

**被問倒時的兜底:** "I don't know yet — that's exactly what a pilot would tell us."(誠實比完整更有說服力。)

---

## 14. 既有素材清單

- `proof-of-understanding-v0.1.html` — v0.1 原型(三階段:材料→房間→收據;Strang 真實板書 15 格+時間戳)。
- `ultimate-proposal-v2.md` — 主提案(The Missing Layer;§2 市場、§4 定律、§6 威脅模型、§9 48 小時 A/B 試點)。
- `lecture-miner/` — 講課挖礦腳本 + Strang 159 格板書 + `states.csv`。
- `hargreaves-evidence-dossier(-zh).md` — Hargreaves 2023 證據檔案("improve upon an AI answer";80 人課堂不可行)。
- `outreach-profiles-pang-hargreaves.md`、`pang-deepdive-demo-plan.md`。
- `cuhk-clear-email-final.md`、`hargreaves-email.md`。

---

## 15. 會後待辦(不管會議結果如何)

1. 24 小時內寄感謝信,重覆三個請求。
2. 把今晚的黑盒矩陣做成可操作 demo(隨機矩陣、4 次查詢、查詢前預測、收據)。
3. 封存檔案庫 demo(10 份假案件文件、腳本圖書館員、預算、收據)。
4. 把新機制(反轉、Hidden/Budget/Commit)寫進 `ultimate-proposal-v2.md` 成 §13。
5. Pang 的「思考便條」郵件(~150 字,"the takeover question")。
6. 若 CLEAR 同意試點:招募訊息、think-aloud 協議卡、記錄表(加一欄「腳本教練失敗」)。

---

*本文件由對話整理;所有效應量和主張都附原始連結,口頭引用前建議點開確認一次。*
