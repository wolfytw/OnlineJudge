# AI 協助解題功能 API 文件

## 功能概述

本系統提供 AI 協助解題功能，支援：
- 即時對話聊天
- 獲取題目提示 (Hint)
- 獲取完整解答 (Solution)
- 對話歷史紀錄
- 使用統計

## API 端點

### 1. AI 對話 API

**POST** `/api/ai/chat/`

發送訊息給 AI 並獲得回應。

**請求參數：**
```json
{
  "problem_id": "A-110",           // 題目 ID (必填)
  "message": "這題該怎麼解？",       // 用戶訊息 (必填)
  "session_id": "uuid-string",     // 對話 ID (可選，第一次留空)
  "message_type": "chat"           // 訊息類型: chat/hint/solution
}
```

**回應：**
```json
{
  "session_id": "uuid-string",
  "user_message": {
    "id": 123,
    "content": "這題該怎麼解？",
    "is_user": true,
    "timestamp": "2025-09-21T12:00:00Z",
    "message_type": "chat"
  },
  "ai_response": {
    "id": 124,
    "content": "這題可以使用動態規劃來解決...",
    "is_user": false,
    "timestamp": "2025-09-21T12:00:05Z",
    "message_type": "chat"
  }
}
```

### 2. 對話列表 API

**GET** `/api/ai/conversations/`

獲取用戶的對話列表。

**查詢參數：**
- `problem_id` (可選): 篩選特定題目的對話

**回應：**
```json
{
  "conversations": [
    {
      "id": 1,
      "session_id": "uuid-string",
      "created_at": "2025-09-21T12:00:00Z",
      "updated_at": "2025-09-21T12:30:00Z",
      "is_active": true,
      "messages": [...]
    }
  ]
}
```

### 3. 對話詳情 API

**GET** `/api/ai/conversations/{session_id}/`

獲取特定對話的完整內容。

**DELETE** `/api/ai/conversations/{session_id}/`

刪除特定對話。

### 4. 使用統計 API

**GET** `/api/ai/usage/`

獲取用戶的 AI 使用統計。

**回應：**
```json
{
  "usage_stats": [
    {
      "date": "2025-09-21",
      "messages_count": 15,
      "tokens_used": 2500
    }
  ]
}
```

### 5. 管理員設定 API

**GET/POST** `/api/admin/ai_config/`

管理員專用，設定 AI 相關配置。

**設定參數：**
```json
{
  "ai_assist_enabled": true,
  "openai_api_key": "sk-...",
  "openai_model": "gpt-3.5-turbo",
  "openai_base_url": "https://api.openai.com/v1",
  "azure_openai_endpoint": "",
  "azure_openai_key": "",
  "azure_openai_deployment_name": ""
}
```

## 前端實作建議

### 1. 題目頁面修改

在題目描述區域右上角加入「啟動 AI 協助」按鈕：

```html
<div class="problem-header">
  <h2>題目標題</h2>
  <button class="ai-assist-btn" @click="toggleAIAssist">
    🤖 啟動 AI 協助
  </button>
</div>
```

### 2. AI 對話區塊

當啟用 AI 協助時，在題目下方顯示對話區塊：

```html
<div class="ai-chat-container" v-if="aiAssistEnabled" style="height: 33vh;">
  <div class="chat-header">
    <span>🤖 AI 協助</span>
    <div class="chat-controls">
      <button @click="getHint">💡 獲取提示</button>
      <button @click="getSolution">📝 查看解答</button>
      <button @click="closeAIAssist">✕</button>
    </div>
  </div>
  
  <div class="chat-messages" ref="chatMessages">
    <div v-for="message in messages" :key="message.id" 
         :class="['message', message.is_user ? 'user' : 'ai']">
      <div class="message-content">{{ message.content }}</div>
      <div class="message-time">{{ formatTime(message.timestamp) }}</div>
    </div>
  </div>
  
  <div class="chat-input">
    <input v-model="userInput" @keyup.enter="sendMessage" 
           placeholder="輸入您的問題..." />
    <button @click="sendMessage">發送</button>
  </div>
</div>
```

### 3. Vue 組件範例

```javascript
export default {
  data() {
    return {
      aiAssistEnabled: false,
      sessionId: null,
      messages: [],
      userInput: '',
      isLoading: false
    }
  },
  
  methods: {
    toggleAIAssist() {
      this.aiAssistEnabled = !this.aiAssistEnabled;
      if (this.aiAssistEnabled && this.messages.length === 0) {
        this.startNewConversation();
      }
    },
    
    async startNewConversation() {
      const welcomeMessage = {
        id: Date.now(),
        content: '您好！我是 AI 助手，可以幫助您理解和解決這道題目。請問有什麼問題嗎？',
        is_user: false,
        timestamp: new Date().toISOString(),
        message_type: 'chat'
      };
      this.messages.push(welcomeMessage);
    },
    
    async sendMessage(messageType = 'chat') {
      if (!this.userInput.trim() && messageType === 'chat') return;
      
      const message = messageType === 'chat' ? this.userInput : 
                     messageType === 'hint' ? '請給我這題的提示' : '請給我這題的完整解答';
      
      this.isLoading = true;
      
      try {
        const response = await this.$http.post('/api/ai/chat/', {
          problem_id: this.problemId,
          message: message,
          session_id: this.sessionId,
          message_type: messageType
        });
        
        this.sessionId = response.data.session_id;
        this.messages.push(response.data.user_message);
        this.messages.push(response.data.ai_response);
        this.userInput = '';
        
        this.$nextTick(() => {
          this.scrollToBottom();
        });
        
      } catch (error) {
        this.$message.error('AI 服務暫時無法使用');
      } finally {
        this.isLoading = false;
      }
    },
    
    getHint() {
      this.sendMessage('hint');
    },
    
    getSolution() {
      this.sendMessage('solution');
    },
    
    scrollToBottom() {
      const container = this.$refs.chatMessages;
      container.scrollTop = container.scrollHeight;
    }
  }
}
```

### 4. CSS 樣式建議

```css
.ai-chat-container {
  border: 1px solid #ddd;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  margin-top: 20px;
}

.chat-header {
  background: #f5f5f5;
  padding: 10px 15px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.message {
  margin-bottom: 15px;
}

.message.user {
  text-align: right;
}

.message.ai {
  text-align: left;
}

.message-content {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 18px;
  max-width: 70%;
  word-wrap: break-word;
}

.message.user .message-content {
  background: #007bff;
  color: white;
}

.message.ai .message-content {
  background: #e9ecef;
  color: #333;
}

.chat-input {
  border-top: 1px solid #ddd;
  padding: 15px;
  display: flex;
  gap: 10px;
}

.chat-input input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
}

.ai-assist-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
```

## 錯誤處理

- API 錯誤：顯示友善的錯誤訊息
- 網路錯誤：提示重試機制
- AI 服務不可用：顯示維護訊息

## 注意事項

1. 需要管理員在後台設定 OpenAI API Key
2. 建議加入使用限制（如每日訊息數量）
3. 可考慮快取常見問題的回答
4. 支援 Markdown 格式的 AI 回應顯示