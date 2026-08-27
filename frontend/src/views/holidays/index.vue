<template>
  <div class="page-container">
    <div class="card-section">
      <div class="flex-between mb-16">
        <h3 style="margin: 0">假期管理</h3>
        <el-button type="primary" :icon="Plus" @click="openCreate">新增假期</el-button>
      </div>
      <div class="mb-16 flex gap-8 flex-center">
        <el-select v-model="filterMember" placeholder="按成员筛选" clearable filterable style="width: 200px">
          <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
        </el-select>
      </div>
      <el-table :data="filtered" border size="small">
        <el-table-column label="成员" width="160">
          <template #default="{ row }">
            <template v-if="row.member">
              <el-avatar :size="20" :style="{ background: row.member.avatar_color, verticalAlign: 'middle' }">{{ row.member.name[0] }}</el-avatar>
              <span class="ml-4">{{ row.member.name }}</span>
            </template>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="typeColor(row.holiday_type)">{{ typeLabel(row.holiday_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始" width="120" />
        <el-table-column prop="end_date" label="结束" width="120" />
        <el-table-column label="天数" width="80" align="center">
          <template #default="{ row }">{{ days(row) }}</template>
        </el-table-column>
        <el-table-column prop="note" label="备注" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑假期' : '新增假期'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="成员" required>
          <el-select v-model="form.member_id" filterable style="width: 100%">
            <el-option v-for="m in members" :key="m.id" :label="m.name + (m.role ? ' - ' + m.role : '')" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.holiday_type" style="width: 100%">
            <el-option v-for="t in types" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="起止" required>
          <el-date-picker
            v-model="form.range"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="-"
            start-placeholder="开始"
            end-placeholder="结束"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.note" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { api, type Member, type Holiday } from '@/api'

const members = ref<Member[]>([])
const holidays = ref<Holiday[]>([])
const filterMember = ref<number | undefined>()
const dialogVisible = ref(false)
const form = ref<any>({ member_id: null, holiday_type: 'personal', range: [], note: '' })

const types = [
  { value: 'personal', label: '事假' },
  { value: 'sick', label: '病假' },
  { value: 'annual', label: '年假' },
  { value: 'public', label: '法定节假日' },
]

const filtered = computed(() =>
  filterMember.value ? holidays.value.filter((h) => h.member_id === filterMember.value) : holidays.value,
)

async function load() {
  members.value = await api.members.list()
  holidays.value = await api.holidays.list()
}

function openCreate() {
  form.value = { member_id: null, holiday_type: 'personal', range: [], note: '' }
  dialogVisible.value = true
}

function openEdit(h: Holiday) {
  form.value = {
    id: h.id, member_id: h.member_id, holiday_type: h.holiday_type,
    range: [h.start_date, h.end_date], note: h.note,
  }
  dialogVisible.value = true
}

async function save() {
  if (!form.value.member_id) return ElMessage.warning('请选择成员')
  if (!form.value.range?.length) return ElMessage.warning('请选择起止日期')
  const payload = {
    member_id: form.value.member_id,
    holiday_type: form.value.holiday_type,
    start_date: form.value.range[0],
    end_date: form.value.range[1],
    note: form.value.note,
  }
  if (form.value.id) await api.holidays.update(form.value.id, payload)
  else await api.holidays.create(payload)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  await load()
}

async function remove(h: Holiday) {
  await ElMessageBox.confirm(`确认删除该假期记录？`, '警告', { type: 'warning' })
  await api.holidays.remove(h.id)
  ElMessage.success('已删除')
  await load()
}

function typeLabel(t: string) {
  return types.find((x) => x.value === t)?.label || t
}
function typeColor(t: string): any {
  const m: Record<string, string> = {
    personal: 'warning', sick: 'danger', annual: 'success', public: 'primary',
  }
  return m[t] || ''
}
function days(h: Holiday) {
  if (!h.start_date || !h.end_date) return 0
  const a = new Date(h.start_date)
  const b = new Date(h.end_date)
  return Math.floor((b.getTime() - a.getTime()) / 86400000) + 1
}
onMounted(load)
</script>

<style scoped>
.ml-4 { margin-left: 4px; }
</style>
