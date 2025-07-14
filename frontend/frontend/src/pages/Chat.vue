<template>
  <div class="p-6 space-y-6 max-w-3xl mx-auto">
    <h2 class="text-2xl font-bold text-center">Multimodal Agent</h2>

    <textarea
      v-model="message"
      class="w-full p-3 border rounded-md"
      rows="4"
      placeholder="请输入您的问题"
    />
    <div class="flex items-center space-x-4">
      <label
        for="file-upload"
        class="cursor-pointer bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded">
        选择文件
      </label>
      <input
        id="file-upload"
        type="file"
        @change="handleFileChange"
        class="hidden"
      />
      <input
        type="text"
        class="flex-1 border rounded px-3 py-2 text-gray-800"
        :value="fileName"
        placeholder="未选择文件"
        readonly
      />
    </div>

    <div v-if="response" class="bg-white p-4 rounded shadow mt-4">
      <p class="text-gray-700 font-medium">回复内容：</p>
      <p class="mt-2 text-gray-900 whitespace-pre-wrap">{{ response }}</p>
    </div>
    <div class="flex justify-between space-x-4">
      <button
          @click="submit"
          :disabled="loading"
          class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded w-full">
          {{ loading ? '正在生成中...' : '发送' }}
      </button>

      <router-link to="/">
      <button class="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded w-full">
        结束对话
      </button>
    </router-link>
    </div>
  </div>



</template>

<script setup lang="ts">
import { ref, computed  } from 'vue'
import axios from 'axios'

axios.defaults.baseURL = 'http://localhost:8000'

axios.defaults.timeout = 10000


const message  = ref<string>('')
const file     = ref<File | null>(null)
const response = ref<string>('')
const loading  = ref<boolean>(false)
const fileName = computed(() => (file.value ? file.value.name : ''))
const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  file.value = target.files && target.files[0] ? target.files[0] : null
}


const pollResult = async (taskId: string) => {
  try {
    const res = await axios.get(`/api/task_result/${taskId}`)

    const payload = res.data.data as {
      status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE'
      result: { response: string } | null
    }

    if (payload.status === 'PENDING' || payload.status === 'STARTED') {

      setTimeout(() => pollResult(taskId), 1000)
    } else if (payload.status === 'SUCCESS' && payload.result) {

      response.value = payload.result.response
      loading.value = false
    } else {

      response.value = `任务状态：${payload.status}`
      loading.value = false
    }
  } catch (err) {
    console.error('轮询失败', err)
    response.value = '轮询接口调用失败'
    loading.value = false
  }
}

const submit = async () => {
  if (!message.value.trim() && !file.value) {
    response.value = '请输入文本或选择文件'
    return
  }

  loading.value = true
  response.value = ''

  const form = new FormData()
  form.append('text', message.value)
  if (file.value) form.append('file', file.value)

  try {
    const res = await axios.post('/api/multimodal_infer_async', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    const taskId = res.data.data.task_id as string

    pollResult(taskId)
  } catch (err) {
    console.error('提交异步任务失败', err)
    response.value = '异步请求失败，请检查后端'
    loading.value = false
  }
}
</script>

<style scoped>

</style>
