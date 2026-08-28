import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';
import path from 'node:path';
// 后端 API 代理：开发态直接走 vite 代理到 FastAPI
export default defineConfig({
    plugins: [
        vue(),
        AutoImport({ resolvers: [ElementPlusResolver()] }),
        Components({ resolvers: [ElementPlusResolver()] }),
    ],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, 'src'),
        },
    },
    server: {
        host: '127.0.0.1',
        port: 5173,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
        },
    },
    build: {
        outDir: 'dist',
        chunkSizeWarningLimit: 4000,
        rollupOptions: {
            output: {
                manualChunks: {
                    vue: ['vue', 'vue-router', 'pinia'],
                    element: ['element-plus'],
                    gantt: ['dhtmlx-gantt'],
                    editor: ['@wangeditor/editor', '@wangeditor/editor-for-vue'],
                    echarts: ['echarts'],
                },
            },
        },
    },
});
