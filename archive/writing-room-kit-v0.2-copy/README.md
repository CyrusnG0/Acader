# The Writing Room — Kit v0.2

AI 時代寫作任務原型,現在有**兩個任務家族**共用同一種收據:封存檔案庫(論文式)+ Matrix Lab(引擎式)。全部 mock、全部本機執行,沒有伺服器。

**核心主張:** 我們不在出口抓人,我們在入口設門。理解是取得證據的鑰匙;收據量的是「asked 和 written 之間的連貫性」。

## 快速開始

1. **玩平台:** 雙擊 `writing-room-v0.2.html`(寫作任務)或 `matrix-lab-v0.2.html`(黑盒矩陣)。兩者都離線。
2. **本機計分:** 需要 Node.js。
   ```
   node scripts/score.js sessions/*.json          # 依 task 自動路由兩個家族
   cat my-session.json | node scripts/score.js -  # stdin 也行;吃 ```json 圍欄
   node scripts/compare.js runs/*.json > report.md # 按 persona 分組的批量報告
   node scripts/similarity.js runs/*.json          # 共謀/複製篩查(3-gram Jaccard)
   ```
3. **引擎自測:** `node scripts/test.js`(14 項 PASS)。

## 檔案

| 檔案 | 是什麼 |
|---|---|
| `writing-room-v0.2.html` | 寫作平台(封存檔案庫+圖書館員+可追溯引用) |
| `matrix-lab-v0.2.html` | 黑盒矩陣任務(隱藏 A、4 次探測、先承諾預測) |
| `scripts/score.js` | 計分引擎+CLI(路由兩個任務家族) |
| `scripts/test.js` | 引擎自測 |
| `scripts/compare.js` | 批量報告:按 persona 分組、成分均值、紅旗頻率 |
| `scripts/similarity.js` | 論文相似度篩查(共謀/複製) |
| `data/corpus.json` · `data/corpus-for-sims.md` | 12 份虛構文件(機讀/人讀) |
| `sessions/wr-*.json` | 寫作家族範例(honest 83 / hybrid 68 / lazy 36 / pasted 9) |
| `sessions/mx-*.json` | 矩陣家族範例(honest 100 / lost 15) |
| `claude-prompts/00–07` | schema、三個寫作 persona、矩陣 persona、紅隊協議、課堂試點包 |
| `memo-can-the-process-tell.md` | 給 CLEAR 的一頁 memo 模板(填結果即用) |

## Coherence score v0.2(寫作家族權重)

| 成分 | 權重 | 量什麼 |
|---|---|---|
| Traceability | .30 | 掛鉤引用是否指向**自己檢索過**的段落 |
| Continuity | .25 | 論文詞彙 vs 問過的問題+拿到的段落 |
| Non-orphan | .10 | 檢索過的段落有沒有用上 |
| Structure | .15 | 貼上事件、寫作爆發(結構,非計時) |
| Trajectory | .10 | DEEP 問題是否隨 session 增加(學習曲線) |
| Citation spread | .10 | 引用分佈在全文,還是堆在結尾 |

Matrix 家族:efficiency .30(有沒有探基向量)· calibration .30(預測準度)· anchoring .25(答案有沒有用探測結果)· commitment .15(先承諾率)。

## 實驗順序(建議)

1. `claude-prompts/01–03`:三臂基線(honest/cheater/hybrid),每臂 ≥5 跑 → `compare.js`。
2. `claude-prompts/06`:紅隊(MIMIC 是重頭戲——把 schema+語料+honest 範例全給它,叫它偽造滿分 session)。**先測再講,結果如實寫進 memo。**
3. `claude-prompts/05`:矩陣家族兩個 persona。
4. `claude-prompts/07`:真實課堂試點包(招募文案、think-aloud 卡、觀察記錄表)。

## 已知限制(會上老實講)

- 圖書館員是腳本+機械檢索(關鍵詞重疊+輕詞幹),不是真 LLM。
- 矩陣家族的 anchoring 是數字比對,粗。
- 手打 AI 文可騙過 Structure;QUERY-BUYER 可能騙過問題訊號——所以收據必須搭配房間檢查(Person & Graesser 1994:回答比問題可靠)。
- 目前分離數字來自**手造 session**;你的模型實驗才是證據。
- MIMIC 攻擊結果未知——這正是要先跑的原因。

## Roadmap(對 CLEAR 講的「下一步」)

- Professor task-compiler UI(填參數表→生成任務)
- Hinge 訊號入權重;每人隨機語料/矩陣 seed
- 真 LLM 圖書館員(同一契約:只回段落,不下結論)
- 班級儀表板(k-anonymity,只看班級層級)
- LMS 導出(LTI 1.3)、Open Badges 3.0 收據

---
Prepared by Cyrus Ng · CS, CUHK — for the CLEAR pilot conversation.
