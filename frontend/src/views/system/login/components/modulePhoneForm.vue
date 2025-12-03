<template>
    <el-form :model="smsForm" :rules="smsRules" ref="smsFormRef" label-width="0" size="large" @keyup.enter="submitPhoneLogin" :disabled="smsLoading">
        <el-form-item prop="mobile">
            <el-input v-model="smsForm.mobile" prefix-icon="phone" clearable placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item prop="code">
            <div style="display:flex;gap:8px;width:100%">
                <el-input v-model="smsForm.code" prefix-icon="message" clearable placeholder="请输入短信验证码" />
                <el-button :disabled="codeCountdown>0 || smsSending" @click="sendPhoneCode" style="min-width:120px">
                    {{ codeCountdown>0 ? `${codeCountdown}s后重发` : (smsSending? '发送中...' : '获取验证码') }}
                </el-button>
            </div>
        </el-form-item>
        <el-form-item v-if="userState.sysConfig.loginCaptcha">
            <el-input type="text" prefix-icon="circle-check" v-model.trim="smsForm.captcha" auto-complete="off" placeholder="验证码">
                <template #append>
                    <lee-img class="login-captcha" :src="image_base" @click="getCaptchas" />
                </template>
            </el-input>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" class="login-btn" style="width: 100%;" :loading="smsLoading" round @click="submitPhoneLogin">登录</el-button>
        </el-form-item>
    </el-form>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Api from '@/api/api'
import { ElMessage } from 'element-plus'
import { setToken, setRefreshToken } from '@/utils/util'
import { useRouter } from 'vue-router'
import { useUserState } from '@/store/userState'

const router = useRouter()
const userState = useUserState()
const API_BASE_URL = window.location.origin

const smsFormRef = ref(null)
const smsForm = ref({ mobile: '', code: '', captcha: '', captchaKey: null })
const smsRules = ref({
    mobile: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
    code: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
})
const smsLoading = ref(false)
const smsSending = ref(false)
const codeCountdown = ref(0)
let codeTimer = null

let image_base = ref(null)

function startCountdown(sec=60){
    codeCountdown.value = sec
    if (codeTimer) clearInterval(codeTimer)
    codeTimer = setInterval(()=>{
        if (codeCountdown.value>0) codeCountdown.value--
        else clearInterval(codeTimer)
    }, 1000)
}

async function getCaptchas(){
    const res = await Api.getCaptcha()
    if (res.code === 2000){
        smsForm.value.captchaKey = res.data.key
        image_base.value = res.data.image_base
    }
}

async function sendPhoneCode(){
    try{
        await smsFormRef.value.validateField('mobile')
    }catch(e){
        return
    }
    if (smsSending.value || codeCountdown.value>0) return
    smsSending.value = true
    const params = { mobile: smsForm.value.mobile }
    if (userState.sysConfig.loginCaptcha){
        params.captcha = smsForm.value.captcha
        params.captchaKey = smsForm.value.captchaKey
    }
    const res = await Api.sendPhoneCode(params)
    smsSending.value = false
    if (res.code === 2000){
        ElMessage.success('验证码已发送')
        startCountdown(60)
    }else{
        ElMessage.error(res.msg || '验证码发送失败')
        getCaptchas()
    }
}

async function submitPhoneLogin(){
    if (smsLoading.value) return
    try{
        smsLoading.value = true
        await smsFormRef.value.validate()
        const res = await Api.phoneLogin({ mobile: smsForm.value.mobile, code: smsForm.value.code })
        if (res.code === 2000){
            setToken('logintoken', res.data.access)
            setRefreshToken('refreshtoken', res.data.refresh)
            await userState.getSystemWebRouter(router)
            ElMessage.success('登录成功')
            window.location.href = API_BASE_URL + '/#/'
        }else{
            ElMessage.error(res.msg || '登录失败')
        }
    }finally{
        smsLoading.value = false
    }
}

onMounted(()=>{
    getCaptchas()
})
</script>

<style scoped>
.login-captcha{
    cursor: pointer;
    height: 38px;
    width: 128px;
    display: block;
    margin: 0px -19px;
    border-top-right-radius: 2px;
    border-bottom-right-radius: 2px;
}
.login-btn{
    margin-top: 10px;
}
</style>

