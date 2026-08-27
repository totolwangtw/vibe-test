<template>
  <el-tag :class="['pri-' + priority]" size="small" effect="light" disable-transitions>
    {{ priority }}
  </el-tag>
</template>
<script setup lang="ts">
defineProps<{ priority: string }>()
</script>
