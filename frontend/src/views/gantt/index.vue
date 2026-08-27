<template>
  <div class="page-container">
    <div class="card-section">
      <div class="flex-between mb-16">
        <h3 style="margin: 0">甘特图</h3>
        <div class="flex gap-8 flex-center">
          <el-radio-group v-model="viewMode" @change="setZoom">
            <el-radio-button value="day">日</el-radio-button>
            <el-radio-button value="week">周</el-radio-button>
            <el-radio-button value="month">月</el-radio-button>
          </el-radio-group>
          <el-checkbox v-model="showCritical">关键路径</el-checkbox>
          <el-button :icon="Refresh" @click="load">刷新</el-button>
        </div>
      </div>
      <div ref="ganttEl" class="gantt-box"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { gantt } from 'dhtmlx-gantt'
import { api, type Member } from '@/api'

const route = useRoute()
const pid = ref(Number(route.params.id))
const ganttEl = ref<HTMLElement>()
const viewMode = ref<'day' | 'week' | 'month'>('week')
const showCritical = ref(false)
const members = ref<Member[]>([])

let mounted = false

function setZoom() {
  if (viewMode.value === 'day') {
    gantt.config.scale_unit = 'day'
    gantt.config.scale_height = 60
    gantt.config.subscales = [{ unit: 'hour', step: 4, format: '%H:%i' }]
    gantt.config.min_column_width = 40
  } else if (viewMode.value === 'week') {
    gantt.config.scale_unit = 'week'
    gantt.config.scale_height = 60
    gantt.config.subscales = [
      { unit: 'week', step: 1, format: (d: Date) => `第 ${gantt.date.weekStart(d).getWeek()} 周` },
      { unit: 'day', step: 1, format: '%j %D' },
    ]
    gantt.config.min_column_width = 50
  } else {
    gantt.config.scale_unit = 'month'
    gantt.config.scale_height = 60
    gantt.config.subscales = [{ unit: 'week', step: 1, format: 'W%W' }]
    gantt.config.min_column_width = 80
  }
  gantt.render()
}

// 周计算 polyfill
;(Date.prototype as any).getWeek = function () {
  const d = new Date(Date.UTC(this.getFullYear(), this.getMonth(), this.getDate()))
  const day = d.getUTCDay() || 7
  d.setUTCDate(d.getUTCDate() + 4 - day)
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
  return Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7)
}

async function load() {
  const res = await api.gantt.data(pid.value)
  members.value = await api.members.list()
  gantt.clearAll()
  gantt.parse({ data: res.tasks, links: res.links })
}

function initGantt() {
  gantt.config.date_format = '%Y-%m-%d %H:%i'
  gantt.config.row_height = 36
  gantt.config.bar_height = 20
  gantt.config.grid_width = 420
  gantt.config.autosize = false
  gantt.config.drag_progress = true
  gantt.config.drag_move = true
  gantt.config.drag_resize = true
  gantt.config.drag_links = true
  gantt.config.smart_rendering = true
  gantt.config.show_progress = true
  gantt.config.fit_tasks = true

  // 中文化
  gantt.i18n.setLocale({
    date: {
      month_full: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
      month_short: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
      day_full: ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'],
      day_short: ['日', '一', '二', '三', '四', '五', '六'],
    },
    labels: {
      new_task: '新任务',
      icon_save: '保存',
      icon_cancel: '取消',
      icon_details: '详情',
      icon_edit: '编辑',
      icon_delete: '删除',
      confirm_closing: '',
      confirm_deleting: '任务将被删除，确定？',
      section_description: '描述',
      section_time: '时间',
      section_type: '类型',
      column_text: '任务名称',
      column_start_date: '开始',
      column_duration: '时长',
      column_add: '',
      link: '链接',
      confirm_link_deleting: '将被删除',
      link_start: ' (开始)',
      link_end: ' (结束)',
      type_task: '任务',
      type_project: '项目',
      type_milestone: '里程碑',
      minutes: '分钟',
      hours: '小时',
      days: '天',
      weeks: '周',
      months: '月',
      years: '年',
    },
  })

  // 自定义列
  gantt.config.columns = [
    { name: 'text', label: '任务', tree: true, width: 200 },
    { name: 'owner_name', label: '责任人', width: 80, align: 'center', template: (t: any) => t.owner_name || '-' },
    { name: 'priority', label: '优先级', width: 60, align: 'center', template: (t: any) => t.priority || '' },
    { name: 'start_date', label: '开始', width: 80, align: 'center' },
  ]

  // 任务条颜色
  gantt.templates.task_class = (start, end, task: any) => {
    if (task.priority === 'P0') return 'gantt-pri-p0'
    if (task.priority === 'P1') return 'gantt-pri-p1'
    return ''
  }
  gantt.templates.task_text = (start, end, task: any) => `${task.text} ${task.progress ? Math.round(task.progress * 100) + '%' : ''}`

  // 拖拽后保存
  gantt.attachEvent('onAfterTaskUpdate', async (id: any, task: any) => {
    await api.gantt.update(pid.value, {
      id: task.id,
      text: task.text,
      start_date: task.start_date ? gantt.templates.date_format(task.start_date, '%Y-%m-%d %H:%i') : undefined,
      duration: task.duration,
      progress: task.progress,
      parent: task.parent,
    })
  })
  gantt.attachEvent('onAfterTaskDrag', async (id: any, mode: any) => {
    const t = gantt.getTask(id)
    await api.gantt.update(pid.value, {
      id: t.id,
      start_date: gantt.templates.date_format(t.start_date, '%Y-%m-%d %H:%i'),
      duration: t.duration,
      progress: t.progress,
    })
  })
  gantt.attachEvent('onAfterLinkAdd', async (_id: any, link: any) => {
    // 简单记录
    ElMessage.info(`已建立依赖：${link.source} → ${link.target}`)
  })

  gantt.init(ganttEl.value as HTMLElement)
  setZoom()
  mounted = true
}

watch(showCritical, (v) => {
  gantt.config.highlight_critical_path = v
  gantt.render()
})

watch(() => route.params.id, (v) => {
  if (v) {
    pid.value = Number(v)
    load()
  }
})

onMounted(async () => {
  initGantt()
  await load()
})

onBeforeUnmount(() => {
  if (mounted) gantt.clearAll()
})
</script>

<style>
@import 'dhtmlx-gantt/codebase/dhtmlxgantt.css';

.gantt-box {
  width: 100%;
  height: calc(100vh - 220px);
  min-height: 480px;
}
.gantt-pri-p0 .gantt_task_content {
  background: #f53f3f !important;
}
.gantt-pri-p1 .gantt_task_content {
  background: #ff7d00 !important;
}
</style>
