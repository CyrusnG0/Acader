# The Writing Room — Kit v0.1

AI 時代的寫作任務原型:封存檔案庫 + 圖書館員 chat(會標記你的問題)+ 可追溯引用 + Coherence receipt。全部 mock、全部瀏覽器內/本機執行,沒有任何伺服器。

**核心主張:** 我們不在出口抓人,我們在入口設門。理解是取得證據的鑰匙;收據量的是「asked 和 written 之間的連貫性」。

## 快速開始

1. **玩平台:** 雙擊 `writing-room-v0.1.html`(離線單一檔案)。順序:COURSE → ARCHIVE → LIBRARIAN(問幾條問題)→ WRITE(插入引用)→ RECEIPT。
2. **本機計分:** 需要 Node.js(你電腦應該已有)。
   ```
   node scripts/score.js sessions/example-honest.json
   node scripts/score.js sessions/*.json        # 全部一次
   cat my-session.json | node scripts/score.js - # stdin 也行
   ```
   直接貼 Claude 的 ```json 圍欄輸出也可以吃。
3. **引擎自測:** `node scripts/test.js`(全部 PASS = 環境正常)。

## 檔案

| 檔案 | 是什麼 |
|---|---|
| `writing-room-v0.1.html` | 平台本體(語料內嵌) |
| `scripts/score.js` | 計分引擎 + CLI(和 HTML 內的引擎同一份抽出) |
| `scripts/test.js` | 引擎自測 |
| `data/corpus.json` | 12 份虛構文件(獨立 JSON 版) |
| `data/corpus-for-sims.md` | 同上、人類可讀版 — 給 Claude 模擬用 |
| `sessions/example-*.json` | 四個範例 session(honest 87 / hybrid 69 / lazy 37 / pasted 5) |
| `claude-prompts/` | 用 Claude 模擬不同學生的完整 prompt + 協議 |

## 用 Claude 模擬學生(第一階段實驗)

看 `claude-prompts/04-batch-protocol.md`。一句話:每個 persona 開新 chat、貼對應 prompt、收 JSON、丟給 score.js、列表比較三組的分數分離。**honest / cheater / hybrid 三臂,每臂至少 5 跑。**

## Coherence score(v1 權重)

| 成分 | 權重 | 量什麼 |
|---|---|---|
| Traceability | .35 | 掛鉤引用是否指向**自己檢索過**的段落(機械驗證,偽造=真的去做) |
| Continuity | .30 | 論文詞彙是否出現在「你問過的問題+你拿到的段落」裡 |
| Non-orphan | .15 | 檢索過的段落有沒有用上 |
| Structure | .20 | 貼上事件、寫作爆發次數(結構,不是計時) |

## 已知限制(會上要老實講)

- 圖書館員是腳本+機械檢索(關鍵詞重疊+輕詞幹),不是真 LLM。
- 手打 AI 文可以騙過 Structure——但成本已接近學習成本。
- 現在的分離數字來自手造 session,**不是結論**;你這階段的實驗才是。
- Hinge(轉折文件)結構已預留、v1 分數未含。
- 要改語料:改 `writing-room-v0.1.html` 內的 `CORPUS` 陣列,`data/` 只是導出副本。

---
Prepared by Cyrus Ng · CS, CUHK — for the CLEAR pilot conversation.
