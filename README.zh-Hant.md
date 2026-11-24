# UAI · 理解模糊意圖

**將不完整、口語化嘅指令，轉成正確嘅下一步。**

[English](README.md) · [技能內容](skills/understanding-ambiguous-intent/SKILL.md) · [驗證記錄](docs/verification.md) · [研究依據](docs/research.md)

UAI 係一個開源、精簡嘅 AI agent 技能。重點係理解你想要嘅結果、
讀取相關上下文、保留限制同更正，再判斷應該直接做、講明假設，定係問一條必要問題。

**v0.3.0 屬於實驗版本。** 暫時唔聲稱比原生模型或其他技能更好。
請先睇實際測試輸出同限制，再判斷係咪適合你。

## 你可以點樣用

| 你講 | 預期行為 |
|---|---|
| 「幫我縮短呢封 email。」 | 直接交出縮短版本。 |
| 「Polish 呢個 prompt：刪除舊備份。」 | 修改 prompt，唔會執行刪除。 |
| 「點解你建議 B？」 | 解釋原因，唔會當你已經揀咗 B。 |
| 「Mobile 都照樣改，其他唔好郁。」 | 沿用相關改動，同時保留限制。 |
| 「幫我寫得自然啲，keep the API names。」 | 自然改寫，保留 API 名稱。 |
| 「繼續。」 | 根據可取得嘅上下文，繼續已授權工作。 |

以上係設計例子，唔係測試成績。

## 安裝

Claude Code 2.1.275 或以上，可喺 Claude Code 入面執行：

```text
/plugin install understanding-ambiguous-intent --marketplace dev-james0723/understanding-ambiguous-intent
```

如想手動安裝或使用其他 host，跟住以下步驟。

核心係文字技能，唔需要 API key、帳戶、伺服器或記憶服務。
可選安裝工具需要 Python 3.10+，而且會拒絕覆蓋現有技能。

```sh
git clone https://github.com/dev-james0723/understanding-ambiguous-intent.git
cd understanding-ambiguous-intent
git checkout v0.3.0
```

支援用戶層 `.agents/skills` 嘅 host：

```sh
python3 scripts/install.py --target "$HOME/.agents/skills" --dry-run
python3 scripts/install.py --target "$HOME/.agents/skills"
```

Claude Code：

```sh
python3 scripts/install.py --target "$HOME/.claude/skills"
```

亦可以手動將 `skills/understanding-ambiguous-intent/` 複製到 host 文件指定嘅
技能目錄。只裝技能資料夾，唔好將評測答案一齊放入去。

如已有 UAI，先自行檢查同備份；安裝工具唔會取代現有版本。
避免同一個 host 同時載入兩套互相競爭嘅 UAI。

Claude Code 亦可用本 repo 嘅 plugin manifest，只為當次 session 載入：

```sh
claude --plugin-dir /absolute/path/to/understanding-ambiguous-intent
```

複製成功、host 載入、技能觸發同實際行為係唔同驗證項目。
詳情見 [相容性](docs/compatibility.md)。

## 核心原則

- 清楚嘅要求直接處理，唔強迫填表或重寫 prompt。
- 先讀相關上下文，避免問返已經答過嘅問題。
- 分清用戶講過嘅內容、已核實事實、推論同未知資料。
- 只為會影響結果嘅缺口提問。
- 保留原有範圍、限制、更正，同仍然適用嘅授權。
- 自然處理中英夾雜、口語同可能嘅語音轉錄錯字。
- 如實區分計劃、嘗試、完成同驗證。

可透過 host 嘅技能選單使用，或要求 agent 使用 Understanding Ambiguous Intent。
支援 dollar-style invocation 嘅 host 可用 `$understanding-ambiguous-intent`。

## 記憶與私隱

UAI 核心只需要當前對話。佢本身唔會收集背景對話、讀取所有歷史、
儲存記憶或同步帳戶。可選上下文整合必須依靠 host 真正提供、
而且已授權嘅能力。見 [adapter 設計契約](docs/context-adapters.md)。

## 本機驗證

```sh
python3 scripts/check.py
python3 -m unittest discover -s tests -v
python3 scripts/evaluate.py --help
```

[評測說明](evals/README.md) 將題目同評分準則分開，支援比較無技能、
簡短指令同 UAI 嘅輸出。結構檢查唔等於行為測試；
純文字測試亦唔等於已驗證真實工具操作。

歡迎提交經匿名化嘅例子，附上必要上下文、預期結果、實際結果、
host 同模型版本。詳見 [貢獻指引](CONTRIBUTING.md)。

## 授權

[MIT License](LICENSE)，James Au。
相關研究同先行專案見 [研究記錄](docs/research.md)。
本專案唔聲稱係第一個或最好嘅意圖理解技能。
