<template>
  <div class="bg-white shadow rounded-lg p-6 space-y-4">
    <div class="text-lg font-semibold">输入信息</div>
    <textarea
      v-model="inputText"
      rows="4"
      class="w-full border rounded p-2"
      placeholder="请输入文本..."
    />

    <div>
      <input type="file" @change="onFileChange" />
    </div>

    <div class="flex space-x-4">
      <button
        class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        @click="submit"
      >
        提交任务
      </button>
      <span v-if="loading" class="text-gray-500">加载中...</span>
    </div>

    <div v-if="response" class="p-4 bg-green-100 rounded">
      <strong>响应结果：</strong>
      <pre class="whitespace-pre-wrap">{{ response }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const inputText = ref('')
const file = ref<File | null>(null)
const loading = ref(false)
const response = ref('')

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    file.value = target.files[0]
  }
}

async function submit() {
  loading.value = true
  response.value = ''

  await new Promise(resolve => setTimeout(resolve, 1000))
  response.value = `已处理文本：${inputText.value}\n文件：${file.value?.name ?? '无'}`
  loading.value = false
}
</script>
