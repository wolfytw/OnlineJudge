# 繁體中文語系支援 - 實作說明

本文件說明如何為 OnlineJudge 2.0 系統新增繁體中文語系支援。

## 已完成的修改

### 1. Django 設定更新 (`oj/settings.py`)

- 新增 `LANGUAGES` 設定，包含英文、簡體中文和繁體中文
- 新增 `LOCALE_PATHS` 指向翻譯檔案位置
- 在 `MIDDLEWARE` 中加入 `django.middleware.locale.LocaleMiddleware` 支援語言切換

```python
LANGUAGES = [
    ('en', 'English'),
    ('zh-hans', '简体中文'),
    ('zh-hant', '繁體中文'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]
```

### 2. 翻譯檔案建立

- 建立 `locale/zh_Hant/LC_MESSAGES/` 目錄結構
- 創建 `django.po` 檔案，包含 164 個常用翻譯字串
- 使用自定義腳本編譯成 `django.mo` 檔案

### 3. 語言切換 API

建立了新的 API 端點：

- `POST /api/admin/set_language/` - 設定用戶語言偏好
- `GET /api/admin/languages/` - 取得可用語言列表

### 4. URL 設定更新

- 在 `oj/urls.py` 中加入國際化支援的 import
- 在 `utils/urls.py` 中新增語言相關的 API 路由

### 5. 編譯工具

創建了 `compile_translations.py` 腳本，用於將 .po 檔案編譯成 .mo 檔案，避免需要完整的 Django 環境。

## 翻譯內容涵蓋範圍

繁體中文翻譯包含以下類別：
- 通用 UI 元素 (首頁、題目、競賽等)
- 題目相關 (描述、輸入輸出、時間限制等)
- 競賽相關 (參賽者、排名、規則等)
- 提交相關 (代碼、語言、結果等)
- 用戶相關 (用戶名、密碼、個人資料等)
- 常見操作 (儲存、取消、編輯等)
- 管理功能 (用戶管理、系統設定等)
- 狀態訊息 (成功、錯誤、驗證等)

## 前端支援說明

根據專案架構分析，此 OnlineJudge 使用分離式架構：
- 後端 (Django): 當前倉庫
- 前端 (Vue): https://github.com/QingdaoU/OnlineJudgeFE

前端的繁體中文支援需要在前端專案中實作，包括：
1. 安裝 vue-i18n
2. 設定語言檔案
3. 整合語言切換功能
4. 呼叫後端的語言 API

## 使用方式

### 設定用戶語言

```bash
curl -X POST http://localhost:8000/api/admin/set_language/ \
  -H "Content-Type: application/json" \
  -d '{"language": "zh-hant"}'
```

### 取得可用語言

```bash
curl http://localhost:8000/api/admin/languages/
```

返回：
```json
{
  "current_language": "en",
  "available_languages": {
    "en": "English",
    "zh-hans": "简体中文", 
    "zh-hant": "繁體中文"
  },
  "languages": [
    {"code": "en", "name": "English", "is_current": true},
    {"code": "zh-hans", "name": "简体中文", "is_current": false},
    {"code": "zh-hant", "name": "繁體中文", "is_current": false}
  ]
}
```

## 後續步驟

1. **前端實作**: 在 Vue 前端專案中實作國際化支援
2. **擴充翻譯**: 根據實際使用情況新增更多翻譯字串
3. **測試**: 完整測試語言切換功能
4. **文件更新**: 更新使用者文件說明多語言功能

## 檔案變更清單

- `oj/settings.py` - Django 國際化設定
- `oj/urls.py` - URL 國際化支援
- `utils/urls.py` - 語言 API 路由
- `utils/i18n_views.py` - 語言切換 API (新檔案)
- `locale/zh_Hant/LC_MESSAGES/django.po` - 繁體中文翻譯 (新檔案)
- `locale/zh_Hant/LC_MESSAGES/django.mo` - 編譯後翻譯檔 (新檔案)
- `compile_translations.py` - 翻譯編譯工具 (新檔案)

## 注意事項

1. 由於使用 API 架構，語言偏好將儲存在用戶 session 中
2. 前端需要配合實作語言切換 UI
3. 某些動態內容可能需要在 Django 模型中加入多語言欄位
4. 建議定期更新翻譯內容以符合功能變更