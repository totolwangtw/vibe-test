import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/BasicLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '工作台', icon: 'Odometer' },
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/projects/index.vue'),
        meta: { title: '项目管理', icon: 'Folder' },
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/projects/detail.vue'),
        meta: { title: '项目详情', hidden: true, parent: 'Projects' },
      },
      {
        path: 'projects/:id/tasks',
        name: 'Tasks',
        component: () => import('@/views/tasks/index.vue'),
        meta: { title: '任务管理', icon: 'List', parent: 'Projects' },
      },
      {
        path: 'projects/:id/gantt',
        name: 'Gantt',
        component: () => import('@/views/gantt/index.vue'),
        meta: { title: '甘特图', icon: 'Calendar', parent: 'Projects' },
      },
      {
        path: 'projects/:id/meetings',
        name: 'Meetings',
        component: () => import('@/views/meetings/index.vue'),
        meta: { title: '会议记录', icon: 'ChatLineSquare', parent: 'Projects' },
      },
      {
        path: 'projects/:id/todos',
        name: 'Todos',
        component: () => import('@/views/todos/index.vue'),
        meta: { title: '待办追踪', icon: 'Checked', parent: 'Projects' },
      },
      {
        path: 'projects/:id/changes',
        name: 'Changes',
        component: () => import('@/views/changes/index.vue'),
        meta: { title: '变更管理', icon: 'Switch', parent: 'Projects' },
      },
      {
        path: 'projects/:id/risks',
        name: 'Risks',
        component: () => import('@/views/risks/index.vue'),
        meta: { title: '风险管理', icon: 'WarnTriangle', parent: 'Projects' },
      },
      {
        path: 'projects/:id/issues',
        name: 'Issues',
        component: () => import('@/views/issues/index.vue'),
        meta: { title: '问题管理', icon: 'Warning', parent: 'Projects' },
      },
      {
        path: 'members',
        name: 'Members',
        component: () => import('@/views/members/index.vue'),
        meta: { title: '成员管理', icon: 'User' },
      },
      {
        path: 'holidays',
        name: 'Holidays',
        component: () => import('@/views/holidays/index.vue'),
        meta: { title: '假期管理', icon: 'Calendar' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/index.vue'),
        meta: { title: '设置', icon: 'Setting' },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
