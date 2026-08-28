<template>
  <div class="csv-toolbar">
    <el-button :icon="Download" size="small" @click="exportCsv">导出 CSV</el-button>
    <el-upload
      :show-file-list="false"
      :before-upload="handleUpload"
      accept=".csv"
    >
      <el-button :icon="Upload" size="small">导入 CSV</el-button>
    </el-upload>
    <el-tooltip content="导入 CSV 文件，会按字段名/列名自动匹配；含 ID 的行会更新，无 ID 的新增。" placement="bottom">
      <el-icon class="tip-icon"><InfoFilled /></el-icon>
    </el-tooltip>
  </div>
</template>

<script setup lang="ts">
import { Download, Upload, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  exportUrl: string  // 完整 url，如 /api/projects/1/tasks/export.csv
  importFn?: (file: File) => Promise<any>  // 可选：自定义导入逻辑
}>()

const emit = defineEmits<{ (e: 'imported'): void }>()

function exportCsv() {
  const a = document.createElement('a')
  a.href = props.exportUrl
  a.download = ''
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

async function handleUpload(file: File) {
  if (!props.importFn) {
    ElMessage.warning('该模块暂不支持导入')
    return false
  }
  try {
    const res = await props.importFn(file)
    const count = res?.imported ?? (Array.isArray(res) ? res.length : 0)
    ElMessage.success(`导入成功，共 ${count} 条`)
    emit('imported')
  } catch (e) {
    // axios 拦截器已提示
  }
  return false
}
</script>

<style scoped>
.csv-toolbar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.tip-icon {
  color: var(--pm-text-secondary);
  cursor: help;
  font-size: 16px;
}
</style>
