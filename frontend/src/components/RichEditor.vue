<template>
  <div class="rich-editor">
    <Toolbar :editor="editorRef" :defaultConfig="toolbarConfig" :mode="mode" />
    <Editor
      :style="{ height: height + 'px', overflowY: 'hidden' }"
      :modelValue="modelValue"
      :defaultConfig="editorConfig"
      :mode="mode"
      @onCreated="handleCreated"
      @onChange="handleChange"
    />
  </div>
</template>

<script setup lang="ts">
import '@wangeditor/editor/dist/css/style.css'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { onBeforeUnmount, ref, shallowRef } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: string
    height?: number
    mode?: 'default' | 'simple'
    placeholder?: string
  }>(),
  { height: 300, mode: 'default', placeholder: '请输入业务需求...' },
)
const emit = defineEmits<{ (e: 'update:modelValue', v: string): void }>()

const editorRef = shallowRef()
const toolbarConfig = {
  excludeKeys: ['group-video', 'fullScreen'],
}
const editorConfig = {
  placeholder: props.placeholder,
  MENU_CONF: {},
}

function handleCreated(editor: any) {
  editorRef.value = editor
}
function handleChange(editor: any) {
  emit('update:modelValue', editor.getHtml())
}
onBeforeUnmount(() => {
  editorRef.value?.destroy()
})
</script>

<style scoped>
.rich-editor {
  border: 1px solid var(--pm-border);
  border-radius: 4px;
  overflow: hidden;
}
</style>
