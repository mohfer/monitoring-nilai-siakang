<template>
    <div
        class="bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-100 dark:border-gray-700 flex flex-col h-full">
        <div class="mb-5">
            <div class="flex justify-between items-center mb-2">
                <span
                    class="px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 border border-transparent"
                    :class="statusClass">
                    <component :is="task.status === 'running' ? Play : Square" :size="12" class="fill-current" />
                    {{ task.status }}
                </span>
                <div class="flex items-center gap-2">
                    <div
                        class="drag-handle cursor-grab active:cursor-grabbing select-none text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                        <GripHorizontal :size="16" />
                    </div>
                    <p class="text-sm text-gray-500 dark:text-gray-400 font-mono">{{ task.login_id }}</p>
                </div>
            </div>
            <h3 class="text-xl font-bold text-gray-800 dark:text-gray-100 leading-tight break-words">{{ task.name }}
            </h3>
        </div>

        <div class="space-y-3 mb-6 flex-grow">
            <div class="flex items-center text-sm">
                <span class="w-24 text-gray-500 dark:text-gray-400 flex-shrink-0 flex items-center gap-1.5">
                    <Activity :size="14" /> Type
                </span>
                <span class="uppercase text-xs font-bold px-2 py-0.5 rounded"
                    :class="task.monitor_type === 'krs' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300' : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'">
                    {{ task.monitor_type === 'krs' ? 'KRS' : 'NILAI' }}
                </span>
            </div>
            <div class="flex items-center text-sm">
                <span class="w-24 text-gray-500 dark:text-gray-400 flex-shrink-0 flex items-center gap-1.5">
                    <Hash :size="14" /> Semester
                </span>
                <span
                    class="font-mono text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded text-xs truncate">{{
                        task.target_semester_code || 'Auto' }}</span>
            </div>
            <div class="flex items-center text-sm">
                <span class="w-24 text-gray-500 dark:text-gray-400 flex-shrink-0 flex items-center gap-1.5">
                    <Timer :size="14" /> Interval
                </span>
                <span class="font-mono text-gray-700 dark:text-gray-200">{{ task.interval }}s</span>
            </div>
            <div class="flex items-center text-sm" v-if="task.pid">
                <span class="w-24 text-gray-500 dark:text-gray-400 flex-shrink-0 flex items-center gap-1.5">
                    <Monitor :size="14" /> PID
                </span>
                <span class="font-mono text-gray-700 dark:text-gray-200">{{ task.pid }}</span>
            </div>
        </div>

        <div
            class="flex flex-wrap items-center justify-between mt-auto pt-4 border-t border-gray-100 dark:border-gray-700 gap-y-3">
            <div class="flex gap-2">
                <button @click="toggleStatus"
                    class="px-4 py-2 rounded-lg text-sm font-semibold transition-all active:scale-95 flex items-center gap-2"
                    :class="task.status === 'running' ? 'bg-red-50 text-red-600 hover:bg-red-100 hover:text-red-700' : 'bg-green-50 text-green-600 hover:bg-green-100 hover:text-green-700'">
                    <Square v-if="task.status === 'running'" :size="16" class="fill-current" />
                    <Play v-else :size="16" class="fill-current" />
                    <span v-if="task.status === 'running'">Stop</span>
                    <span v-else>Start</span>
                </button>
                <button @click="showLogs"
                    class="text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                    title="View Logs">
                    <FileText :size="20" />
                </button>
                <button @click="showData"
                    class="text-gray-500 hover:text-green-600 dark:text-gray-400 dark:hover:text-green-400 p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                    title="View Data">
                    <Table :size="20" />
                </button>
                <button @click="$emit('clone')"
                    class="text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                    title="Clone Task">
                    <Copy :size="20" />
                </button>
            </div>
            <div class="flex gap-1">
                <button @click="$emit('edit')"
                    class="text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                    title="Edit">
                    <Edit :size="20" />
                </button>
                <button @click="$emit('delete')"
                    class="text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                    title="Delete">
                    <Trash2 :size="20" />
                </button>
            </div>
        </div>

        <div v-if="showingLogs" @click.self="closeLogs"
            class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 backdrop-blur-sm p-4 transition-all">
            <div
                class="bg-white dark:bg-gray-900 rounded-xl w-full max-w-4xl h-[85vh] flex flex-col shadow-2xl overflow-hidden border border-gray-200 dark:border-gray-700">
                <div
                    class="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
                    <h3 class="font-bold text-lg dark:text-white flex items-center gap-2">
                        <FileText :size="20" class="text-blue-600 dark:text-blue-400" />
                        Logs: <span class="text-gray-700 dark:text-gray-300">{{ task.name }}</span>
                    </h3>
                    <div class="flex items-center gap-1">
                        <button @click="clearLogs"
                            class="text-gray-500 hover:text-red-600 dark:hover:text-red-400 transition p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded full mr-2"
                            title="Clear Logs">
                            <Trash2 :size="18" />
                        </button>
                        <button @click="closeLogs"
                            class="text-gray-500 hover:text-gray-700 dark:hover:text-white transition p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded full"
                            title="Close">
                            <X :size="20" />
                        </button>
                    </div>
                </div>
                <div class="flex-grow relative bg-gray-950">
                    <div class="absolute inset-0 overflow-auto p-4 custom-scrollbar" ref="logContainer">
                        <div v-if="logs === 'Loading...'"
                            class="flex items-center justify-center h-full text-gray-500 gap-2">
                            <Loader2 :size="24" class="animate-spin" /> Loading logs...
                        </div>
                        <pre v-else
                            class="font-mono text-xs sm:text-sm text-green-400 whitespace-pre-wrap leading-relaxed">{{ logs }}</pre>
                    </div>
                </div>
                <div
                    class="p-3 bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center text-xs sm:text-sm">
                    <div class="flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                        <span class="text-gray-500 dark:text-gray-400">Live updating every 2s</span>
                    </div>
                    <span class="text-gray-400 hidden sm:inline">Last 200 lines</span>
                </div>
            </div>
        </div>

        <div v-if="showingData" @click.self="showingData = false"
            class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 backdrop-blur-sm p-4 transition-all">
            <div
                class="bg-white dark:bg-gray-900 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden border border-gray-200 dark:border-gray-700">
                <div
                    class="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
                    <h3 class="font-bold text-lg dark:text-white flex items-center gap-2">
                        <Table :size="20" class="text-green-600 dark:text-green-400" />
                        Scraped Data: <span class="text-gray-700 dark:text-gray-300">{{ task.name }}</span>
                        <div class="ml-4 flex items-center gap-1 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
                            <button @click="clearData"
                                class="p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-500 hover:text-red-600 dark:hover:text-red-400 transition"
                                title="Reset Data">
                                <Trash2 :size="16" />
                            </button>
                            <div class="w-px h-4 bg-gray-300 dark:bg-gray-600"></div>
                            <button @click="refreshData" :disabled="isRefreshing"
                                class="p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 text-blue-600 dark:text-blue-400 transition disabled:opacity-50"
                                title="Fetch Data Now">
                                <RotateCw :size="16" :class="{ 'animate-spin': isRefreshing }" />
                            </button>
                        </div>
                    </h3>
                    <button @click="showingData = false"
                        class="text-gray-500 hover:text-gray-700 dark:hover:text-white transition p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded full">
                        <X :size="20" />
                    </button>
                </div>

                <div class="flex-grow overflow-auto p-4 custom-scrollbar bg-white dark:bg-gray-900">
                    <div v-if="!hasDataDisplay"
                        class="text-center text-gray-500 py-10 flex flex-col items-center gap-3">
                        <Table :size="48" class="text-gray-300" />
                        <p>No data found.</p>
                        <p class="text-sm text-gray-400">Start the task to scrape data from Siakang.</p>
                    </div>
                    <div v-else class="flex flex-col gap-5">
                        <div v-if="resultData && resultData.nama"
                            class="bg-blue-50 dark:bg-gray-800 p-4 rounded-lg flex flex-col md:flex-row justify-between md:items-center gap-2 border border-blue-100 dark:border-gray-700">
                            <div>
                                <h4 class="font-bold text-gray-800 dark:text-white">{{ resultData.nama }}</h4>
                                <p class="text-sm text-gray-500 dark:text-gray-400 font-mono">{{ resultData.nim }}</p>
                            </div>
                            <div class="flex gap-4">
                                <div class="text-center">
                                    <span class="block text-xs uppercase text-gray-500 dark:text-gray-400">Total
                                        SKS</span>
                                    <span class="font-bold text-lg dark:text-blue-300 text-blue-700">
                                        {{ resultData.total_sks !== undefined ? resultData.total_sks : '-' }}
                                    </span>
                                </div>
                                <div class="text-center">
                                    <span class="block text-xs uppercase text-gray-500 dark:text-gray-400">Total
                                        Matkul</span>
                                    <span class="font-bold text-lg dark:text-green-300 text-green-700">{{
                                        courseData.length }}</span>
                                </div>
                            </div>
                        </div>

                        <div v-if="gpaData.length > 0"
                            class="grid grid-cols-1 md:grid-cols-2 gap-4 top-0 z-10 bg-white dark:bg-gray-900 pb-2">
                            <div v-for="(item, idx) in gpaData" :key="idx"
                                class="bg-gradient-to-br from-blue-50 to-white dark:from-blue-900/40 dark:to-gray-800 border border-blue-100 dark:border-blue-800 p-4 rounded-xl flex justify-between items-center shadow-sm">
                                <span class="text-blue-800 dark:text-blue-300 font-semibold text-sm">{{ item.matkul
                                }}</span>
                                <span class="text-3xl font-bold text-blue-700 dark:text-blue-400 font-mono">{{
                                    item.nilai }}</span>
                            </div>
                        </div>

                        <div class="rounded-lg border border-gray-200 dark:border-gray-700 overflow-x-auto"
                            v-if="task.monitor_type === 'krs'">
                            <div class="p-4 bg-white dark:bg-gray-900">
                                <h4 class="font-bold mb-3 text-gray-800 dark:text-white flex items-center gap-2">
                                    <Activity :size="16" class="text-purple-600" /> Target Courses Status
                                </h4>
                                <div v-if="krsCourseStatus.length > 0">
                                    <ul class="space-y-2">
                                        <li v-for="(item, idx) in krsCourseStatus" :key="idx"
                                            class="flex items-center gap-2 p-3 border rounded-lg transition-colors duration-300"
                                            :class="item.found
                                                ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                                                : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'">
                                            <div class="h-2 w-2 rounded-full flex-shrink-0"
                                                :class="item.found ? 'bg-green-500' : 'bg-red-500'"></div>
                                            <span class="font-medium flex-grow"
                                                :class="item.found ? 'text-gray-700 dark:text-green-300' : 'text-gray-700 dark:text-red-300'">
                                                {{ item.name }}
                                            </span>
                                            <span class="text-xs px-2 py-0.5 rounded font-bold uppercase"
                                                :class="item.found ? 'bg-green-200 text-green-800 dark:bg-green-800 dark:text-green-200' : 'bg-red-200 text-red-800 dark:bg-red-800 dark:text-red-200'">
                                                {{ item.found ? 'Found' : 'Missing' }}
                                            </span>
                                        </li>
                                    </ul>
                                </div>
                                <div v-else
                                    class="text-gray-500 italic p-4 text-center border border-dashed rounded-lg">
                                    No target courses configured.
                                </div>
                            </div>
                        </div>

                        <div class="rounded-lg border border-gray-200 dark:border-gray-700 overflow-x-auto" v-else>
                            <table
                                class="w-full text-sm text-left text-gray-500 dark:text-gray-400 min-w-[500px] md:min-w-full">
                                <thead
                                    class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-800 dark:text-gray-300">
                                    <tr>
                                        <th class="px-6 py-3">Mata Kuliah</th>
                                        <th class="px-6 py-3 text-center">SKS</th>
                                        <th class="px-6 py-3 text-center">Nilai</th>
                                        <th class="px-6 py-3 text-center">Mutu</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="(item, idx) in courseData" :key="idx"
                                        class="bg-white border-b dark:bg-gray-900 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                                        <td class="px-6 py-4 font-medium text-gray-900 dark:text-white">
                                            {{ item.matkul }}
                                        </td>
                                        <td
                                            class="px-6 py-4 text-center text-xs font-mono text-gray-500 dark:text-gray-400">
                                            {{ item.sks ? item.sks : '-' }}
                                        </td>
                                        <td class="px-6 py-4 text-center">
                                            <span class="font-mono text-gray-800 dark:text-gray-200"
                                                :class="{ 'px-2 py-1 rounded bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300 font-bold': item.nilai !== '---' }">
                                                {{ item.nilai }}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4 text-center">
                                            <span v-if="item.mutu !== '---'"
                                                class="font-bold text-blue-600 dark:text-blue-400">{{ item.mutu
                                                }}</span>
                                            <span v-else>-</span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <div
                    class="p-3 bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 text-xs text-center text-gray-500">
                    Showing latest data from local storage
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, ref, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import { Play, Square, FileText, Edit, Trash2, X, Loader2, Monitor, Timer, Hash, Table, RotateCw, Copy, GripHorizontal, Activity } from 'lucide-vue-next'

const props = defineProps(['task'])
const emit = defineEmits(['edit', 'delete', 'refresh', 'clone'])

const showingLogs = ref(false)
const showingData = ref(false)
const isRefreshing = ref(false)
const logs = ref('Loading...')
const resultData = ref(null)
const logContainer = ref(null)
const API_URL = '/api'
let logInterval = null

const courseData = computed(() => {
    if (!resultData.value || !resultData.value.nilai) return []
    return resultData.value.nilai.filter(item => !item.matkul.includes('Indeks Prestasi'))
})

const gpaData = computed(() => {
    if (!resultData.value) return []
    if (resultData.value.ips && resultData.value.ipk) {
        return [
            { matkul: "Indeks Prestasi (IP)", nilai: resultData.value.ips },
            { matkul: "Indeks Prestasi Kumulatif (IPK)", nilai: resultData.value.ipk }
        ]
    }
    if (Array.isArray(resultData.value)) {
        return resultData.value.filter(item => item.matkul.includes('Indeks Prestasi'))
    }
    return []
})

const krsCourseStatus = computed(() => {
    if (props.task.monitor_type !== 'krs') return []

    let targets = []
    try {
        if (props.task.target_courses) {
            targets = JSON.parse(props.task.target_courses)
            if (!Array.isArray(targets)) targets = []
        }
    } catch (e) {
        targets = []
    }

    const found = resultData.value && resultData.value.found ? resultData.value.found : []

    return targets.map(course => ({
        name: course,
        found: found.includes(course)
    }))
})

const hasDataDisplay = computed(() => {
    if (props.task.monitor_type === 'krs') {
        const t = props.task.target_courses
        return t && t !== '[]' && t !== 'null'
    }
    return resultData.value && (resultData.value.nilai || (Array.isArray(resultData.value) && resultData.value.length > 0))
})

const statusClass = computed(() => {
    switch (props.task.status) {
        case 'running': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
        case 'stopped': return 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
        default: return 'bg-yellow-100 text-yellow-800'
    }
})

const toggleStatus = async () => {
    try {
        const action = props.task.status === 'running' ? 'stop' : 'start'
        await axios.post(`${API_URL}/tasks/${props.task.id}/${action}`)
        emit('refresh')
    } catch (e) {
        alert('Failed to change status: ' + (e.response?.data?.message || e.message))
    }
}

const showLogs = async () => {
    showingLogs.value = true
    logs.value = 'Loading...'
    await refreshLogs()
    logInterval = setInterval(refreshLogs, 2000)
}

const showData = async () => {
    showingData.value = true
    resultData.value = null
    try {
        const res = await axios.get(`${API_URL}/tasks/${props.task.id}/data`)
        resultData.value = res.data.data
        if (Array.isArray(resultData.value) && resultData.value.length === 0) {
            resultData.value = null
        }
    } catch (e) {
        console.error(e)
    }
}

const refreshData = async () => {
    if (isRefreshing.value) return
    isRefreshing.value = true
    try {
        await axios.post(`${API_URL}/tasks/${props.task.id}/refresh`)

        const res = await axios.get(`${API_URL}/tasks/${props.task.id}/data`)
        resultData.value = res.data.data
        if (Array.isArray(resultData.value) && resultData.value.length === 0) {
            resultData.value = null
        }
    } catch (e) {
        alert('Failed to refresh: ' + (e.response?.data?.message || e.message))
    } finally {
        isRefreshing.value = false
    }
}

const clearLogs = async () => {
    if (!confirm('Clear all logs for this task?')) return
    try {
        await axios.delete(`${API_URL}/tasks/${props.task.id}/logs`)
        refreshLogs()
    } catch (e) {
        alert('Failed to clear logs')
    }
}

const clearData = async () => {
    if (!confirm('Delete scraped data for this task?')) return
    try {
        await axios.delete(`${API_URL}/tasks/${props.task.id}/data`)
        resultData.value = null
    } catch (e) {
        alert('Failed to clear data')
    }
}

const closeLogs = () => {
    showingLogs.value = false
    if (logInterval) {
        clearInterval(logInterval)
        logInterval = null
    }
}

const refreshLogs = async () => {
    try {
        const res = await axios.get(`${API_URL}/tasks/${props.task.id}/logs`)
        const newLogs = res.data.data || "No logs available."

        const container = logContainer.value
        const isNearBottom = container ? (container.scrollHeight - Math.ceil(container.scrollTop) - container.clientHeight < 50) : true

        logs.value = newLogs

        if (isNearBottom) {
            nextTick(() => {
                if (logContainer.value) {
                    logContainer.value.scrollTop = logContainer.value.scrollHeight
                }
            })
        }
    } catch (e) {
        logs.value = "Failed to load logs."
    }
}

onUnmounted(() => {
    if (logInterval) clearInterval(logInterval)
})
</script>
