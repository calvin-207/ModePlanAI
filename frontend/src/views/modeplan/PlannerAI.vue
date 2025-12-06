<template>
  <div class="ai-assistant-container">
    <el-row :gutter="15">
      <el-col :span="18">
        <el-card shadow="never" class="chat-card">
          <div class="chat-header">
            <div class="chat-title">
              <el-avatar :size="40" class="chat-avatar">
                <el-icon><ChatLineSquare /></el-icon>
              </el-avatar>
              <div class="chat-title-text">
                <div class="name">AI 企划专家</div>
                <div class="desc">智能分析·专业建议</div>
              </div>
            </div>
            <el-select v-model="model" size="small" style="width: 140px">
              <el-option label="GPT-4" value="gpt-4" />
              <el-option label="GPT-4o" value="gpt-4o" />
              <el-option label="GPT-4o-mini" value="gpt-4o-mini" />
            </el-select>
          </div>
          <div class="chat-body" ref="chatBodyRef">
            <div
              v-for="(m, idx) in messages"
              :key="idx"
              :class="['msg-item', m.role === 'user' ? 'is-user' : 'is-assistant']"
            >
              <div class="msg-avatar">
                <el-avatar :size="30">
                  <el-icon v-if="m.role==='assistant'"><ChatLineSquare /></el-icon>
                  <el-icon v-else><User /></el-icon>
                </el-avatar>
              </div>
              <div class="msg-bubble">
                <div class="msg-content" v-html="renderMarkdown(m.content)"></div>
                <div class="msg-actions">
                  <el-button text size="small" :icon="CopyDocument" @click="copyMessage(m)">复制</el-button>
                  <el-button v-if="m.role==='assistant'" text size="small" :icon="RefreshRight" @click="regenerate(m)">重试</el-button>
                </div>
              </div>
            </div>
            <div v-if="sending" class="msg-item is-assistant loading">
              <div class="msg-avatar">
                <el-avatar :size="30">
                  <el-icon><ChatLineSquare /></el-icon>
                </el-avatar>
              </div>
              <div class="msg-bubble">
                <el-skeleton :rows="1" animated style="width: 240px" />
              </div>
            </div>
          </div>
          <div class="chat-input">
            <el-input
              v-model="input"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 8 }"
              maxlength="2000"
              show-word-limit
              placeholder="输入您的企划问题，Enter 发送，Shift+Enter 换行"
              @keydown.enter="onEnterKey"
            />
            <div class="input-toolbar">
              <div class="left">
                <el-button text size="small" @click="clearSession">清空对话</el-button>
              </div>
              <div class="right">
                <el-button v-if="sending" type="warning" size="small" icon="VideoPause" @click="stop">停止</el-button>
                <el-button v-else type="primary" size="small" :disabled="!input.trim()" :loading="sending" @click="send" icon="Promotion">发送</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="side-header">
            <span>快捷提问</span>
          </div>
          <div class="quick-questions">
            <el-button
              v-for="(q,i) in quickPrompts"
              :key="i"
              class="quick-btn"
              @click="usePrompt(q)"
              plain
              >{{ q }}</el-button>
          </div>
        </el-card>
        <el-card shadow="hover" style="margin-top: 12px">
          <div class="side-header">
            <span>当前企划信息</span>
          </div>
          <el-descriptions :column="1" size="small" border>
            <el-descriptions-item label="季度">{{ planning.season }}</el-descriptions-item>
            <el-descriptions-item label="主题">{{ planning.theme }}</el-descriptions-item>
            <el-descriptions-item label="产品SKU">{{ planning.sku }}</el-descriptions-item>
            <el-descriptions-item label="目标销售额">{{ planning.target }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        <el-card shadow="hover" class="tips-card">
          <div class="side-header">
            <span>提示</span>
          </div>
          <div class="tips-content">
            您可以向AI助手咨询任何关于企划、设计、生产、销售的问题，助手会基于行业经验和数据分析提供专业建议。
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
 </template>

 <script setup>
 import { ref, reactive, nextTick, onMounted } from 'vue'
import Api from '@/api/conversation'
 import { ElMessage } from 'element-plus'
 import { ChatLineSquare, User, Promotion, CopyDocument, RefreshRight, VideoPause } from '@element-plus/icons-vue'

 const model = ref('gpt-4')
const input = ref('')
const sending = ref(false)
const chatBodyRef = ref(null)
const conversationId = ref('')
let abortCtl = null

  const messages = ref([
    {
      role: 'assistant',
      content: '您好！我是ModePlanAI智能企划助手，专注于服装行业的企划咨询。我可以帮您：\n• 分析市场趋势和流行色彩\n• 规划产品线和款式组合\n• 优化生产排期和供应链\n• 制定销售策略和目标\n• 提供行业洞察和建议\n\n请问有什么可以帮助到您的？'
    }
  ])

 const quickPrompts = ref([
   '2025春夏流行趋势',
   '产品线优化建议',
   '生产排期规划',
   '定价策略分析'
 ])

 const planning = reactive({
   season: '2025 春夏',
   theme: '都市自然',
   sku: 280,
   target: '¥8,500万'
 })

 function renderMarkdown(text) {
   const raw = String(text || '')
     .replace(/<br\s*\/?>(\s*)/gi, '\n')
     .replace(/<[^>]+>/g, '')
   const s = raw
     .replace(/&/g, '&amp;')
     .replace(/</g, '&lt;')
     .replace(/>/g, '&gt;')
     .replace(/\n/g, '<br/>')
   return s
 }

 function scrollToBottom() {
   if (!chatBodyRef.value) return
   chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
 }

  function usePrompt(q) {
    input.value = q
    nextTick(() => send())
  }

  function onEnterKey(e){
    if(e.shiftKey){
      return
    }
    e.preventDefault()
    send()
  }

  function stop(){
    if(abortCtl){
      abortCtl.abort()
      abortCtl = null
    }
    sending.value = false
  }

  function clearSession(){
    messages.value = [
      {
        role: 'assistant',
        content: '您好！我是ModePlanAI智能企划助手，专注于服装行业的企划咨询。我可以帮您：<br/>• 分析市场趋势和流行色彩<br/>• 规划产品线和款式组合<br/>• 优化生产排期和供应链<br/>• 制定销售策略和目标<br/>• 提供行业洞察和建议<br/><br/>请问有什么可以帮助到您的？'
      }
    ]
  }

  async function copyMessage(m){
    try{
      await navigator.clipboard.writeText(String(m.content||''))
      ElMessage.success('已复制')
    }catch(err){
      ElMessage.warning('复制失败')
    }
  }

  function regenerate(m){
    input.value = (typeof m.content === 'string') ? m.content : ''
    nextTick(()=>send())
  }
 async function send() {
   const content = input.value.trim()
   if (!content || sending.value) return
   input.value = ''
   messages.value.push({ role: 'user', content })
   sending.value = true
   const assistant = { role: 'assistant', content: '' }
   messages.value.push(assistant)
   try {
     const { controller, responsePromise } = Api.postChatStream({ question: content, conversation_id: conversationId.value || undefined })
     abortCtl = controller
     const resp = await responsePromise
     if(!resp.ok || !resp.body){
       ElMessage.warning('对话失败')
       return
     }
     const reader = resp.body.getReader()
     const decoder = new TextDecoder()
     let done = false
     let buffer = ''
     while(!done){
       const { value, done: d } = await reader.read()
       done = d
       if(value){
         buffer += decoder.decode(value, { stream: true })
         const parts = buffer.split(/\r?\n/)
         buffer = parts.pop() || ''
         for(const line of parts){
           const t = line.trim()
           if(!t) continue
           try{
             const obj = JSON.parse(t)
             if(typeof obj.answer === 'string'){
               assistant.content = obj.answer
             }
             if(obj.conversation_id){
               conversationId.value = obj.conversation_id
             }
           }catch(_){
           }
         }
         await nextTick()
         scrollToBottom()
       }
     }
   } catch (e) {
     ElMessage.error('对话接口异常')
   } finally {
     abortCtl = null
     sending.value = false
     await nextTick()
     scrollToBottom()
   }
 }

 onMounted(() => {
   nextTick(() => scrollToBottom())
 })
 </script>

 <style lang="scss" scoped>
.ai-assistant-container { padding: 10px; }
.chat-card { height: calc(100vh - 120px); display: flex; flex-direction: column; }
.chat-card :deep(.el-card__body){ height: 100%; display: flex; flex-direction: column; padding-bottom: 0; }
.chat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
 .chat-title { display: flex; align-items: center; }
 .chat-avatar { background: var(--el-color-primary); color: #fff; }
 .chat-title-text { margin-left: 10px; }
 .chat-title-text .name { font-size: 16px; font-weight: 600; }
 .chat-title-text .desc { font-size: 12px; color: #909399; }
.chat-body { flex: 1; overflow: auto; padding: 10px 0 14px; }
 .msg-item { display: flex; align-items: flex-start; margin: 10px 0; }
 .msg-item.is-user { flex-direction: row-reverse; }
 .msg-avatar { width: 40px; display: flex; justify-content: center; }
 .msg-bubble { max-width: 80%; padding: 10px 12px; border-radius: 10px; background: var(--el-bg-color); color: var(--el-text-color-primary); }
 .msg-item.is-user .msg-bubble { background: #ecf5ff; color: #303133; }
 .msg-item.is-assistant .msg-bubble { background: #f5f7fa; }
 .msg-content { white-space: pre-wrap; word-break: break-word; }
.chat-input { border-top: 1px solid var(--el-border-color-light); padding-top: 10px; background: var(--el-bg-color); }
.input-toolbar { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.input-toolbar .left { display: flex; align-items: center; gap: 6px; }
.input-toolbar .right { display: flex; align-items: center; gap: 6px; }
.msg-actions { margin-top: 6px; display: flex; gap: 6px; opacity: 0; transition: opacity .2s; }
.msg-bubble:hover .msg-actions { opacity: 1; }
 .side-header { font-weight: 600; margin-bottom: 10px; }
.quick-questions { display: flex; flex-direction: column; gap: 8px; }
.quick-btn { width: 100%; text-align: left; display: flex; justify-content: flex-start; align-items: center; }
.quick-btn :deep(.el-button__text){ width: 100%; text-align: left; }
 .tips-card { margin-top: 12px; }
 .tips-content { font-size: 12px; color: #606266; line-height: 1.6; }
 </style>
