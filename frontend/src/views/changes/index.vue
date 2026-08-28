<template>
  <div class="page-container">
    <div class="card-section">
      <div class="flex-between mb-16">
        <div class="flex gap-12 flex-center">
          <h3 style="margin: 0">变更管理</h3>
          <el-radio-group v-model="filterStatus">
            <el-radio-button value="">全部</el-radio-button>
            <el-radio-button value="draft">草稿</el-radio-button>
            <el-radio-button value="review">评审中</el-radio-button>
            <el-radio-button value="approved">已批准</el-radio-button>
            <el-radio-button value="implemented">已实施</el-radio-button>
            <el-radio-button value="closed">已关闭</el-radio-button>
          </el-radio-group>
        </div>
        <div class="flex gap-8 flex-center">
          <CsvToolbar
            :export-url="api.changes.exportCsv(pid)"
            :import-fn="(f: File) => api.changes.importCsv(pid, f)"
            @imported="load"
          />
          <el-button type="primary" :icon="Plus" @click="openCreate">新建变更</el-button>
        </div>
      </div>

      <el-table :data="filtered" border size="small">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="title" label="变更标题" min-width="200">
          <template #default="{ row }">
            <span class="link" @click="openEdit(row)">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="typeColor(row.change_type)">{{ typeLabel(row.change_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="影响" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="levelColor(row.impact_level)" effect="dark">{{ row.impact_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提出人" width="100">
          <template #default="{ row }">{{ row.requester?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="负责人" width="100">
          <template #default="{ row }">{{ row.owner?.name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="request_date" label="提出日期" width="110" />
        <el-table-column prop="plan_date" label="计划实施" width="110" />
        <el-table-column prop="implement_date" label="实施日期" width="110" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!filtered.length" description="暂无变更记录" />
    </div>

    <el-drawer v-model="dialogVisible" size="60%" :title="form.id ? '编辑变更' : '新建变更'" :destroy-on-close="true">
      <el-form :model="form" label-width="100px">
        <el-form-item label="变更标题" required><el-input v-model="form.title" placeholder="简述本次变更内容" /></el-form-item>
        <el-row>
          <el-col :span="8">
            <el-form-item label="变更类型">
              <el-select v-model="form.change_type" style="width: 100%">
                <el-option v-for="t in typeOpts" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="影响级别">
              <el-select v-model="form.impact_level" style="width: 100%">
                <el-option label="高 (H)" value="H" />
                <el-option label="中 (M)" value="M" />
                <el-option label="低 (L)" value="L" />
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
            <el-form-item label="提出人">
              <el-select v-model="form.requester_id" clearable filterable style="width: 100%">
                <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="负责人">
              <el-select v-model="form.owner_id" clearable filterable style="width: 100%">
                <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="8">
            <el-form-item label="提出日期">
              <el-date-picker v-model="form.request_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="计划实施">
              <el-date-picker v-model="form.plan_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="实施日期">
              <el-date-picker v-model="form.implement_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="变更描述">
          <RichEditor v-model="form.content_html" :height="220" placeholder="详细描述本次变更的背景、内容、范围..." />
        </el-form-item>
        <el-form-item label="影响分析">
          <RichEditor v-model="form.impact_html" :height="180" placeholder="变更对项目进度、成本、质量、风险等方面的影响..." />
        </el-form-item>
        <el-form-item label="回滚方案">
          <RichEditor v-model="form.rollback_html" :height="180" placeholder="变更失败或异常时的回滚步骤与预案..." />
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
import { api, type Change, type Member } from '@/api'
import RichEditor from '@/components/RichEditor.vue'
import CsvToolbar from '@/components/CsvToolbar.vue'

const route = useRoute()
const pid = computed(() => Number(route.params.id))

const changes = ref<Change[]>([])
const members = ref<Member[]>([])
const filterStatus = ref('')
const dialogVisible = ref(false)
const form = ref<any>({})

const typeOpts = [
  { value: 'standard', label: '标准变更' },
  { value: 'normal', label: '普通变更' },
  { value: 'emergency', label: '紧急变更' },
]
const statusOpts = [
  { value: 'draft', label: '草稿' },
  { value: 'review', label: '评审中' },
  { value: 'approved', label: '已批准' },
  { value: 'implemented', label: '已实施' },
  { value: 'closed', label: '已关闭' },
  { value: 'rejected', label: '已拒绝' },
]

const filtered = computed(() =>
  filterStatus.value ? changes.value.filter((c) => c.status === filterStatus.value) : changes.value,
)

async function load() {
  changes.value = await api.changes.list(pid.value)
  members.value = await api.members.list()
}

function openCreate() {
  form.value = {
    project_id: pid.value,
    title: '',
    content_html: '',
    change_type: 'normal',
    status: 'draft',
    impact_level: 'M',
    requester_id: null,
    owner_id: null,
    request_date: new Date().toISOString().slice(0, 10),
    plan_date: '',
    implement_date: '',
    impact_html: '',
    rollback_html: '',
  }
  dialogVisible.value = true
}

function openEdit(c: Change) {
  form.value = { ...c }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.title) return ElMessage.warning('请输入变更标题')
  const payload = {
    title: form.value.title,
    content_html: form.value.content_html,
    change_type: form.value.change_type,
    status: form.value.status,
    impact_level: form.value.impact_level,
    requester_id: form.value.requester_id || null,
    owner_id: form.value.owner_id || null,
    request_date: form.value.request_date || null,
    plan_date: form.value.plan_date || null,
    implement_date: form.value.implement_date || null,
    impact_html: form.value.impact_html,
    rollback_html: form.value.rollback_html,
  }
  if (form.value.id) await api.changes.update(form.value.id, payload)
  else await api.changes.create({ ...payload, project_id: pid.value })
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await load()
}

async function remove(c: Change) {
  await ElMessageBox.confirm(`确认删除变更「${c.title}」？`, '警告', { type: 'warning' })
  await api.changes.remove(c.id)
  ElMessage.success('已删除')
  await load()
}

function typeLabel(t: string) {
  return typeOpts.find((x) => x.value === t)?.label || t
}
function typeColor(t: string): any {
  const m: Record<string, string> = { standard: '', normal: 'warning', emergency: 'danger' }
  return m[t] || ''
}
function statusLabel(s: string) {
  return statusOpts.find((x) => x.value === s)?.label || s
}
function statusColor(s: string): any {
  const m: Record<string, string> = {
    draft: 'info', review: 'warning', approved: 'primary',
    implemented: 'success', closed: '', rejected: 'danger',
  }
  return m[s] || ''
}
function levelColor(l: string): any {
  const m: Record<string, string> = { H: 'danger', M: 'warning', L: 'success' }
  return m[l] || ''
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
