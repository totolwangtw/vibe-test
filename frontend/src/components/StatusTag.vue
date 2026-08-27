<template>
  <el-tag :class="['st-' + status]" size="small" effect="light" disable-transitions>
    {{ label }}
  </el-tag>
</template>
<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ status: string }>()
const MAP: Record<string, string> = {
  todo: '待开始',
  doing: '进行中',
  done: '已完成',
  blocked: '阻塞',
  open: '待办',
  in_progress: '进行中',
  active: '进行中',
  paused: '已暂停',
  done_project: '已结束',
}
const label = computed(() => MAP[props.status] || props.status)
</script>
