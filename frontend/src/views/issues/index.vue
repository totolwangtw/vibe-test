<template>
  <div class="page-container">
    <div class="card-section">
      <div class="flex-between mb-16">
        <div class="flex gap-12 flex-center">
          <h3 style="margin: 0">问题管理</h3>
          <el-radio-group v-model="filterStatus">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="open">待处理</el-radio-button>
            <el-radio-button value="in_progress">处理中</el-radio-button>
            <el-radio-button value="resolved">已解决</el-radio-button>
            <el-radio-button value="closed">已关闭</el-radio-button>
          </el-radio-group>
        </div>
        <div class="flex gap-8 flex-center">
          <CsvToolbar
            :export-url="api.issues.exportCsv(pid)"
            :import-fn="(f: File) => api.issues.importCsv(pid, f)"
            @imported="load"
          />
          <el-button type="primary" :icon="Plus" @click="openCreate">新建问题</el-button>
        </div>
      </div>

      <el-table :data="filtered" border size="small">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="title" label="问题标题" min-width="220">
          <template #default="{ row }">
            <span class="link" @click="openEdit(row)">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">{{ typeLabel(row.issue_type) }}</template>
        </el-table-column>
        <el-table-column label="优先级" width="80" align="center">
          <template #default="{ row }"><PriorityTag :priority="row.priority" /></template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="负责人" width="100">
          <template #default="{ row }">{{ row.owner?.name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="raised_date" label="提出日期" width="110" />
        <el-table-column prop="due_date" label="截止日期" width="110" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!filtered.length" description="暂无问题记录" />
    </div>

    <el-drawer v-model="dialogVisible" size="60%" :title="form.id ? '编辑问题' : '新建问题'" :destroy-on-close="true">
      <el-form :model="form" label-width="100px">
        <el-form-item label="问题标题" required><el-input v-model="form.title" placeholder="简述问题" /></el-form-item>
        <el-row>
          <el-col :span="8">
            <el-form-item label="问题类型">
              <el-select v-model="form.issue_type" style="width: 100%">
                <el-option v-for="t in typeOpts" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option v-for="p in PRI_OPTS" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option v-for="s in statusOpts" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="8">
            <el-form-item label="提出日期">
              <el-date-picker v-model="form.raised_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="截止日期">
              <el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="负责人">
          <el-select v-model="form.owner_id" clearable filterable style="width: 100%">
            <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题描述">
          <RichEditor v-model="form.description_html" :height="220" placeholder="描述问题的现象、复现步骤、影响范围..." />
        </el-form-item>
        <el-form-item label="解决方案">
          <RichEditor v-model="form.resolution_html" :height="220" placeholder="记录问题的解决方案、处理过程、验证结果..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { api, type Issue, type Member } from '@/api'
import RichEditor from '@/components/RichEditor.vue'
import CsvToolbar from '@/components/CsvToolbar.vue'
import PriorityTag from '@/components/PriorityTag.vue'

const route = useRoute()
const pid = computed(() => Number(route.params.id))
const PRI_OPTS = ['P0', 'P1', 'P2', 'P3']

const issues = ref<Issue[]>([])
const members = ref<Member[]>([])
const filterStatus = ref('')
const dialogVisible = ref(false)
const form = ref<any>({})

const typeOpts = [
  { value: 'bug', label: '缺陷 Bug' },
  { value: 'requirement', label: '需求问题' },
  { value: 'technical', label: '技术问题' },
  { value: 'resource', label: '资源问题' },
  { value: 'process', label: '流程问题' },
  { value: 'other', label: '其他' },
]
const statusOpts = [
  { value: 'open', label: '待处理' },
  { value: 'in_progress', label: '处理中' },
  { value: 'resolved', label: '已解决' },
  { value: 'closed', label: '已关闭' },
]

const filtered = computed(() =>
  filterStatus.value ? issues.value.filter((i) => i.status === filterStatus.value) : issues.value,
)

async function load() {
  issues.value = await api.issues.list(pid.value)
  members.value = await api.members.list()
}

function openCreate() {
  form.value = {
    project_id: pid.value,
    title: '',
    description_html: '',
    issue_type: 'bug',
    status: 'open',
    priority: 'P2',
    owner_id: null,
    raised_date: new Date().toISOString().slice(0, 10),
    due_date: '',
    resolution_html: '',
  }
  dialogVisible.value = true
}

function openEdit(i: Issue) {
  form.value = { ...i }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.title) return ElMessage.warning('请输入问题标题')
  const payload = {
    title: form.value.title,
    description_html: form.value.description_html,
    issue_type: form.value.issue_type,
    status: form.value.status,
    priority: form.value.priority,
    owner_id: form.value.owner_id || null,
    raised_date: form.value.raised_date || null,
    due_date: form.value.due_date || null,
    resolution_html: form.value.resolution_html,
  }
  if (form.value.id) await api.issues.update(form.value.id, payload)
  else await api.issues.create({ ...payload, project_id: pid.value })
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await load()
}

async function remove(i: Issue) {
  await ElMessageBox.confirm(`确认删除问题「${i.title}」？`, '警告', { type: 'warning' })
  await api.issues.remove(i.id)
  ElMessage.success('已删除')
  await load()
}

function typeLabel(t: string) {
  return typeOpts.find((x) => x.value === t)?.label || t
}
function statusLabel(s: string) {
  return statusOpts.find((x) => x.value === s)?.label || s
}
function statusColor(s: string): any {
  const m: Record<string, string> = {
    open: 'danger', in_progress: 'warning', resolved: 'success', closed: '',
  }
  return m[s] || ''
}

watch(pid, load)
onMounted(load)
</script>

<style scoped>
.link {
  color: var(--pm-primary);
  cursor: pointer;
  &:hover { text-decoration: underline; }
}
</style>
