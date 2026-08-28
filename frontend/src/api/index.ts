import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err?.response?.data?.detail || err?.message || '请求失败'
    ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    return Promise.reject(err)
  },
)

export default http

// ---------- 类型 ----------
export interface Member {
  id: number
  name: string
  avatar_color?: string
  email?: string
  role?: string
}
export interface Project {
  id: number
  name: string
  code?: string
  description?: string
  status: string
  priority: string
  start_date?: string
  end_date?: string
  color: string
  progress: number
  member_count?: number
  task_count?: number
}
export interface Attachment {
  id: number
  filename: string
  size: number
  mime_type?: string
  uploaded_at?: string
}
export interface Task {
  id: number
  project_id: number
  parent_id?: number | null
  title: string
  content_html?: string
  status: string
  priority: string
  task_type: string
  start_date?: string
  end_date?: string
  planned_hours: number
  actual_hours: number
  progress: number
  owner_id?: number
  owner?: Member
  sort_order: number
  is_starred: boolean
  color?: string
  collapsed: boolean
  children?: Task[]
  attachments?: Attachment[]
  tags?: { id: number; name: string; color: string }[]
}
export interface Meeting {
  id: number
  project_id: number
  title: string
  meeting_type: string
  meeting_date: string
  start_time?: string
  end_time?: string
  host_id?: number
  host?: Member
  attendees: number[]
  content_html?: string
  todo_count?: number
}
export interface Todo {
  id: number
  project_id: number
  meeting_id?: number
  title: string
  content?: string
  mention_ids: number[]
  assignee_id?: number
  assignee?: Member
  mentions?: Member[]
  status: string
  priority: string
  due_date?: string
}
export interface Holiday {
  id: number
  member_id: number
  member?: Member
  project_id?: number
  holiday_type: string
  start_date: string
  end_date: string
  note?: string
}
export interface Change {
  id: number
  project_id: number
  title: string
  content_html?: string
  change_type: string
  status: string
  impact_level: string
  requester_id?: number
  requester?: Member
  owner_id?: number
  owner?: Member
  request_date?: string
  plan_date?: string
  implement_date?: string
  impact_html?: string
  rollback_html?: string
}
export interface Risk {
  id: number
  project_id: number
  title: string
  description_html?: string
  risk_type: string
  probability: string
  impact: string
  level: string
  status: string
  owner_id?: number
  owner?: Member
  due_date?: string
  mitigation_html?: string
}
export interface Issue {
  id: number
  project_id: number
  title: string
  description_html?: string
  issue_type: string
  status: string
  priority: string
  owner_id?: number
  owner?: Member
  raised_date?: string
  due_date?: string
  resolution_html?: string
}

// ---------- API ----------
export const api = {
  // members
  members: {
    list: () => http.get<any, Member[]>('/members'),
    create: (d: Partial<Member>) => http.post<any, Member>('/members', d),
    update: (id: number, d: Partial<Member>) => http.put<any, Member>(`/members/${id}`, d),
    remove: (id: number) => http.delete(`/members/${id}`),
  },
  // projects
  projects: {
    list: () => http.get<any, Project[]>('/projects'),
    get: (id: number) => http.get<any, Project>(`/projects/${id}`),
    create: (d: any) => http.post<any, Project>('/projects', d),
    update: (id: number, d: any) => http.put<any, Project>(`/projects/${id}`, d),
    remove: (id: number) => http.delete(`/projects/${id}`),
    members: (id: number) => http.get<any, Member[]>(`/projects/${id}/members`),
    addMember: (pid: number, mid: number, role?: string) =>
      http.post(`/projects/${pid}/members/${mid}`, null, { params: { role } }),
    removeMember: (pid: number, mid: number) => http.delete(`/projects/${pid}/members/${mid}`),
    holidays: (id: number) => http.get<any, Holiday[]>(`/projects/${id}/holidays`),
  },
  // tasks
  tasks: {
    tree: (pid: number) => http.get<any, Task[]>(`/projects/${pid}/tasks/tree`),
    list: (pid: number) => http.get<any, Task[]>(`/projects/${pid}/tasks`),
    get: (id: number) => http.get<any, Task>(`/tasks/${id}`),
    create: (d: any) => http.post<any, Task>('/tasks', d),
    update: (id: number, d: any) => http.put<any, Task>(`/tasks/${id}`, d),
    remove: (id: number) => http.delete(`/tasks/${id}`),
    batch: (pid: number, items: any[]) => http.put(`/projects/${pid}/tasks/batch`, items),
    worklogs: (tid: number) => http.get<any, any[]>(`/tasks/${tid}/worklogs`),
    addWorklog: (tid: number, d: any) => http.post<any, any>(`/tasks/${tid}/worklogs`, d),
  },
  // attachments
  attachments: {
    list: (tid: number) => http.get<any, Attachment[]>(`/tasks/${tid}/attachments`),
    upload: (tid: number, file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      return http.post<any, Attachment>(`/tasks/${tid}/attachments`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
    download: (id: number) => `/api/attachments/${id}/download`,
    remove: (id: number) => http.delete(`/attachments/${id}`),
  },
  // meetings
  meetings: {
    list: (pid: number) => http.get<any, Meeting[]>(`/projects/${pid}/meetings`),
    get: (id: number) => http.get<any, Meeting>(`/meetings/${id}`),
    create: (d: any) => http.post<any, Meeting>('/meetings', d),
    update: (id: number, d: any) => http.put<any, Meeting>(`/meetings/${id}`, d),
    remove: (id: number) => http.delete(`/meetings/${id}`),
  },
  // todos
  todos: {
    list: (pid: number, status?: string) =>
      http.get<any, Todo[]>(`/projects/${pid}/todos`, { params: { status } }),
    create: (d: any) => http.post<any, Todo>('/todos', d),
    update: (id: number, d: any) => http.put<any, Todo>(`/todos/${id}`, d),
    remove: (id: number) => http.delete(`/todos/${id}`),
    mentions: () => http.get<any, Member[]>('/todos/mention-candidates'),
  },
  // holidays
  holidays: {
    list: (params?: any) => http.get<any, Holiday[]>('/holidays', { params }),
    create: (d: any) => http.post<any, Holiday>('/holidays', d),
    update: (id: number, d: any) => http.put<any, Holiday>(`/holidays/${id}`, d),
    remove: (id: number) => http.delete(`/holidays/${id}`),
  },
  // dashboard
  dashboard: {
    overview: () => http.get<any, any>('/dashboard'),
    project: (pid: number) => http.get<any, any>(`/dashboard/projects/${pid}`),
  },
  // gantt
  gantt: {
    data: (pid: number) => http.get<any, { tasks: any[]; links: any[] }>(`/projects/${pid}/gantt`),
    update: (pid: number, d: any) => http.put(`/projects/${pid}/gantt`, d),
  },
  // changes
  changes: {
    list: (pid: number) => http.get<any, Change[]>(`/projects/${pid}/changes`),
    get: (id: number) => http.get<any, Change>(`/changes/${id}`),
    create: (d: any) => http.post<any, Change>('/changes', d),
    update: (id: number, d: any) => http.put<any, Change>(`/changes/${id}`, d),
    remove: (id: number) => http.delete(`/changes/${id}`),
    exportCsv: (pid: number) => `/api/projects/${pid}/changes/export.csv`,
    importCsv: (pid: number, file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      return http.post<any, any>(`/projects/${pid}/changes/import.csv`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
  },
  // risks
  risks: {
    list: (pid: number) => http.get<any, Risk[]>(`/projects/${pid}/risks`),
    get: (id: number) => http.get<any, Risk>(`/risks/${id}`),
    create: (d: any) => http.post<any, Risk>('/risks', d),
    update: (id: number, d: any) => http.put<any, Risk>(`/risks/${id}`, d),
    remove: (id: number) => http.delete(`/risks/${id}`),
    exportCsv: (pid: number) => `/api/projects/${pid}/risks/export.csv`,
    importCsv: (pid: number, file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      return http.post<any, any>(`/projects/${pid}/risks/import.csv`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
  },
  // issues
  issues: {
    list: (pid: number) => http.get<any, Issue[]>(`/projects/${pid}/issues`),
    get: (id: number) => http.get<any, Issue>(`/issues/${id}`),
    create: (d: any) => http.post<any, Issue>('/issues', d),
    update: (id: number, d: any) => http.put<any, Issue>(`/issues/${id}`, d),
    remove: (id: number) => http.delete(`/issues/${id}`),
    exportCsv: (pid: number) => `/api/projects/${pid}/issues/export.csv`,
    importCsv: (pid: number, file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      return http.post<any, any>(`/projects/${pid}/issues/import.csv`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
  },
  // csv 导入导出（通用模块）
  csv: {
    exportTasks: (pid: number) => `/api/projects/${pid}/tasks/export.csv`,
    importTasks: (pid: number, file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      return http.post<any, any>(`/projects/${pid}/tasks/import.csv`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
    exportTodos: (pid: number) => `/api/projects/${pid}/todos/export.csv`,
    importTodos: (pid: number, file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      return http.post<any, any>(`/projects/${pid}/todos/import.csv`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
    exportMeetings: (pid: number) => `/api/projects/${pid}/meetings/export.csv`,
    exportMembers: () => `/api/members/export.csv`,
    importMembers: (file: File) => {
      const fd = new FormData()
      fd.append('file', file)
      return http.post<any, any>('/members/import.csv', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    },
    exportHolidays: () => `/api/holidays/export.csv`,
  },
}
