<template>
  <div class="page-container">
    <div class="card-section">
      <div class="flex-between mb-16">
        <div class="flex gap-12 flex-center">
          <h3 style="margin: 0">任务管理</h3>
          <el-tag size="small" effect="plain">{{ pid }}</el-tag>
          <el-input v-model="filterText" placeholder="搜索任务标题" :prefix-icon="Search" clearable style="width: 220px" />
          <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px">
            <el-option v-for="s in STATUS_OPTS" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
          <el-select v-model="filterOwner" placeholder="责任人" clearable filterable style="width: 140px">
            <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </div>
        <div class="flex gap-8">
          <el-button :icon="Expand" @click="expandAll(true)">全部展开</el-button>
          <el-button :icon="Fold" @click="expandAll(false)">全部折叠</el-button>
          <el-button type="primary" :icon="Plus" @click="openCreate(null)">新建任务</el-button>
        </div>
      </div>

      <el-table
        :data="filteredTree"
        row-key="id"
        border
        default-expand-all
        :tree-props="{ children: 'children' }"
        :expand-row-keys="expandedKeys"
        @expand-change="onExpandChange"
        size="small"
        class="task-table"
      >
        <el-table-column prop="title" label="任务" min-width="280">
          <template #default="{ row }">
            <div class="task-title-cell">
              <el-icon v-if="row.is_starred" color="#E6A23C" class="mr-4"><Star /></el-icon>
              <span class="task-title" @click="openEdit(row)">{{ row.title }}</span>
              <el-tag v-for="t in row.tags" :key="t.id" :color="t.color" effect="dark" size="small" class="ml-4">{{ t.name }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-select v-model="row.status" size="small" @change="(v) => patchTask(row, { status: v })">
              <el-option v-for="s in STATUS_OPTS" :key="s.value" :label="s.label" :value="s.value" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="90">
          <template #default="{ row }">
            <el-select v-model="row.priority" size="small" @change="(v) => patchTask(row, { priority: v })">
              <el-option v-for="p in PRI_OPTS" :key="p" :label="p" :value="p" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="责任人" width="130">
          <template #default="{ row }">
            <el-select v-model="row.owner_id" size="small" filterable clearable placeholder="无" @change="(v) => patchTask(row, { owner_id: v })">
              <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id">
                <el-avatar :size="18" :style="{ background: m.avatar_color, verticalAlign: 'middle' }">{{ m.name[0] }}</el-avatar>
                <span style="margin-left: 6px">{{ m.name }}</span>
              </el-option>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="起止时间" width="220">
          <template #default="{ row }">
            <el-date-picker
              v-model="row._range"
              type="daterange"
              size="small"
              value-format="YYYY-MM-DD"
              range-separator="-"
              start-placeholder="开始"
              end-placeholder="结束"
              style="width: 100%"
              @change="(v: any) => patchDate(row, v)"
            />
          </template>
        </el-table-column>
        <el-table-column label="进度" width="120">
          <template #default="{ row }">
            <el-slider v-model="row.progress" :show-tooltip="false" @change="(v) => patchTask(row, { progress: v })" />
          </template>
        </el-table-column>
        <el-table-column label="工时(h)" width="130">
          <template #default="{ row }">
            <span class="text-sm">{{ row.actual_hours }} / {{ row.planned_hours }}</span>
            <el-button text size="small" :icon="Clock" @click="openWorklog(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">详情</el-button>
            <el-button text size="small" @click="openCreate(row)">+ 子任务</el-button>
            <el-button text type="danger" size="small" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 任务详情抽屉 -->
    <el-drawer v-model="editVisible" size="60%" :title="form.id ? '编辑任务' : '新建任务'" :destroy-on-close="true">
      <el-form :model="form" label-width="90px">
        <el-form-item label="任务标题" required>
          <el-input v-model="form.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-row>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option v-for="s in STATUS_OPTS" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option v-for="p in PRI_OPTS" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="任务类型">
              <el-select v-model="form.task_type" style="width: 100%">
                <el-option v-for="t in TYPE_OPTS" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="责任人">
              <el-select v-model="form.owner_id" filterable clearable style="width: 100%">
                <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="开始">
              <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束">
              <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="计划工时">
              <el-input-number v-model="form.planned_hours" :min="0" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="进度">
              <el-slider v-model="form.progress" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="星标">
          <el-switch v-model="form.is_starred" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="form.color" />
        </el-form-item>
        <el-form-item label="标签">
          <div class="tags-editor">
            <el-tag
              v-for="(t, i) in form.tags"
              :key="i"
              :color="t.color"
              effect="dark"
              closable
              @close="form.tags.splice(i, 1)"
            >{{ t.name }}</el-tag>
            <el-input
              v-if="tagInputVisible"
              v-model="tagInput"
              size="small"
              style="width: 100px"
              @keyup.enter="addTag"
              @blur="addTag"
            />
            <el-button v-else size="small" @click="tagInputVisible = true">+ 标签</el-button>
          </div>
        </el-form-item>
        <el-form-item label="业务需求">
          <RichEditor v-model="form.content_html" :height="240" />
        </el-form-item>
        <el-form-item label="附件">
          <el-upload
            :show-file-list="false"
            :before-upload="(f: any) => uploadAttachment(f)"
            multiple
          >
            <el-button :icon="Upload">上传附件</el-button>
          </el-upload>
          <div class="att-list">
            <div v-for="a in form.attachments" :key="a.id" class="att-item">
              <el-icon><Document /></el-icon>
              <a :href="attUrl(a.id)" target="_blank">{{ a.filename }}</a>
              <span class="text-sm text-secondary">{{ (a.size / 1024).toFixed(1) }} KB</span>
              <el-button text type="danger" size="small" :icon="Delete" @click="removeAtt(a.id)" />
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTask">保存</el-button>
      </template>
    </el-drawer>

    <!-- 工时记录 -->
    <el-dialog v-model="worklogVisible" title="工时记录" width="640px">
      <el-form :model="worklogForm" label-width="80px" class="mb-16">
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="日期"><el-date-picker v-model="worklogForm.log_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="成员">
              <el-select v-model="worklogForm.member_id" clearable style="width: 100%">
                <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="工时"><el-input-number v-model="worklogForm.hours" :min="0" :step="0.5" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="worklogForm.comment" /></el-form-item>
      </el-form>
      <el-button type="primary" @click="addWorklog">添加工时</el-button>
      <el-table :data="worklogs" size="small" class="mt-16">
        <el-table-column prop="log_date" label="日期" width="120" />
        <el-table-column label="成员" width="100">
          <template #default="{ row }">{{ memberName(row.member_id) }}</template>
        </el-table-column>
        <el-table-column prop="hours" label="工时" width="80" />
        <el-table-column prop="comment" label="备注" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Expand, Fold, Star, Clock, Upload, Document, Delete,
} from '@element-plus/icons-vue'
import { api, type Task, type Member } from '@/api'
import RichEditor from '@/components/RichEditor.vue'

const route = useRoute()
const pid = computed(() => Number(route.params.id))

const STATUS_OPTS = [
  { value: 'todo', label: '待开始' },
  { value: 'doing', label: '进行中' },
  { value: 'done', label: '已完成' },
  { value: 'blocked', label: '阻塞' },
]
const PRI_OPTS = ['P0', 'P1', 'P2', 'P3']
const TYPE_OPTS = [
  { value: 'task', label: '任务' },
  { value: 'milestone', label: '里程碑' },
  { value: 'bug', label: '缺陷' },
  { value: 'story', label: '故事' },
]

const tree = ref<Task[]>([])
const members = ref<Member[]>([])
const expandedKeys = ref<number[]>([])
const filterText = ref('')
const filterStatus = ref('')
const filterOwner = ref<number | undefined>()

const editVisible = ref(false)
const form = ref<any>({})
const tagInputVisible = ref(false)
const tagInput = ref('')

const worklogVisible = ref(false)
const worklogs = ref<any[]>([])
const worklogForm = ref<any>({ task_id: null, member_id: undefined, hours: 1, log_date: new Date().toISOString().slice(0, 10), comment: '' })

// 给每条任务增加 _range 用于表格内的日期范围
function withRange(t: Task): any {
  const arr: any[] = []
  for (const c of t.children || []) arr.push(withRange(c))
  return { ...t, _range: t.start_date && t.end_date ? [t.start_date, t.end_date] : [], children: arr }
}

async function load() {
  const data = await api.tasks.tree(pid.value)
  tree.value = data.map(withRange)
  expandedKeys.value = collectIds(data)
  members.value = await api.members.list()
}

function collectIds(tasks: Task[]): number[] {
  const ids: number[] = []
  for (const t of tasks) {
    ids.push(t.id)
    if (t.children?.length) ids.push(...collectIds(t.children))
  }
  return ids
}

const filteredTree = computed(() => {
  const filter = (nodes: any[]): any[] => {
    const result: any[] = []
    for (const n of nodes) {
      const matchText = !filterText.value || n.title.includes(filterText.value)
      const matchStatus = !filterStatus.value || n.status === filterStatus.value
      const matchOwner = !filterOwner.value || n.owner_id === filterOwner.value
      const children = filter(n.children || [])
      if ((matchText && matchStatus && matchOwner) || children.length) {
        result.push({ ...n, children })
      }
    }
    return result
  }
  return filter(tree.value)
})

function expandAll(open: boolean) {
  expandedKeys.value = open ? collectIds(tree.value) : []
}

function onExpandChange(row: any, expanded: any[]) {
  const ids = expanded.map((r: any) => r.id)
  if (ids.includes(row.id) && !expandedKeys.value.includes(row.id)) expandedKeys.value.push(row.id)
  else expandedKeys.value = expandedKeys.value.filter((i) => i !== row.id)
}

function openCreate(parent: Task | null) {
  form.value = {
    project_id: pid.value,
    parent_id: parent?.id || null,
    title: '', content_html: '', status: 'todo', priority: 'P2',
    task_type: 'task', start_date: '', end_date: '',
    planned_hours: 0, actual_hours: 0, progress: 0,
    owner_id: undefined, is_starred: false, color: '', tags: [], attachments: [],
  }
  editVisible.value = true
}

function openEdit(t: Task) {
  form.value = JSON.parse(JSON.stringify(t))
  editVisible.value = true
}

async function saveTask() {
  if (!form.value.title) return ElMessage.warning('请输入任务标题')
  const payload = {
    title: form.value.title,
    content_html: form.value.content_html,
    status: form.value.status,
    priority: form.value.priority,
    task_type: form.value.task_type,
    start_date: form.value.start_date || null,
    end_date: form.value.end_date || null,
    planned_hours: form.value.planned_hours,
    progress: form.value.progress,
    owner_id: form.value.owner_id || null,
    parent_id: form.value.parent_id || null,
    is_starred: form.value.is_starred,
    color: form.value.color || null,
    tags: form.value.tags,
  }
  if (form.value.id) {
    await api.tasks.update(form.value.id, payload)
  } else {
    await api.tasks.create(payload)
  }
  ElMessage.success('保存成功')
  editVisible.value = false
  await load()
}

async function patchTask(t: any, patch: any) {
  await api.tasks.update(t.id, patch)
}

async function patchDate(t: any, range: any) {
  if (range && range.length === 2) {
    await api.tasks.update(t.id, { start_date: range[0], end_date: range[1] })
    t.start_date = range[0]
    t.end_date = range[1]
  } else {
    await api.tasks.update(t.id, { start_date: null, end_date: null })
    t.start_date = null
    t.end_date = null
  }
}

async function remove(t: Task) {
  await ElMessageBox.confirm(`确认删除任务「${t.title}」及其所有子任务？`, '警告', { type: 'warning' })
  await api.tasks.remove(t.id)
  ElMessage.success('已删除')
  await load()
}

function addTag() {
  if (tagInput.value) {
    form.value.tags.push({ name: tagInput.value, color: '#909399' })
  }
  tagInput.value = ''
  tagInputVisible.value = false
}

async function uploadAttachment(file: File) {
  if (!form.value.id) {
    ElMessage.warning('请先保存任务再上传附件')
    return false
  }
  await api.attachments.upload(form.value.id, file)
  form.value.attachments = await api.attachments.list(form.value.id)
  ElMessage.success('上传成功')
  return false
}

function attUrl(id: number) {
  return api.attachments.download(id)
}

async function removeAtt(id: number) {
  await api.attachments.remove(id)
  form.value.attachments = await api.attachments.list(form.value.id)
}

function memberName(id?: number) {
  return members.value.find((m) => m.id === id)?.name || '-'
}

async function openWorklog(t: Task) {
  worklogForm.value = { task_id: t.id, member_id: t.owner_id, hours: 1, log_date: new Date().toISOString().slice(0, 10), comment: '' }
  worklogs.value = await api.tasks.worklogs(t.id)
  worklogVisible.value = true
}

async function addWorklog() {
  await api.tasks.addWorklog(worklogForm.value.task_id, worklogForm.value)
  ElMessage.success('已添加工时')
  worklogs.value = await api.tasks.worklogs(worklogForm.value.task_id)
  await load()
}

watch(pid, load)
onMounted(load)
</script>

<style scoped lang="scss">
.task-title-cell {
  display: flex;
  align-items: center;
  gap: 4px;
}
.mr-4 { margin-right: 4px; }
.ml-4 { margin-left: 4px; }
.task-title {
  cursor: pointer;
  color: var(--pm-primary);
  &:hover { text-decoration: underline; }
}
.tags-editor {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}
.att-list { margin-top: 8px; }
.att-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  a { color: var(--pm-primary); }
}
</style>
