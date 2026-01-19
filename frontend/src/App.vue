<template>
    <div class="min-h-screen p-4 md:p-8 transition-colors duration-300 bg-gray-50 dark:bg-gray-900 font-sans"
        :class="{ 'dark': isDark }">
        <div class="max-w-7xl mx-auto">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 class="text-2xl md:text-3xl font-bold text-gray-800 dark:text-white flex items-center gap-3">
                        <LayoutDashboard :size="32" class="text-blue-600 dark:text-blue-400" />
                        Siakang Monitor Dashboard
                    </h1>
                    <p class="text-gray-500 dark:text-gray-400 mt-1 ml-1">Manage your scraping instances</p>
                </div>
                <div class="flex gap-3 w-full md:w-auto">
                    <button @click="toggleDark"
                        class="p-2.5 rounded-full bg-white dark:bg-gray-800 text-gray-600 dark:text-yellow-400 shadow hover:shadow-md transition border border-gray-100 dark:border-gray-700">
                        <Sun v-if="isDark" :size="20" />
                        <Moon v-else :size="20" />
                    </button>
                    <button @click="openModal()"
                        class="flex-1 md:flex-none justify-center bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-medium transition shadow-lg shadow-blue-500/30 flex items-center gap-2">
                        <Plus :size="20" /> New Task
                    </button>
                </div>
            </div>

            <draggable v-model="tasks" item-key="id"
                class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6" @start="isDragging = true"
                @end="onDragEnd" handle=".drag-handle" :animation="200" :force-fallback="true" :gpu-acceleration="false"
                ghost-class="opacity-0" fallback-class="rub-float-effect">
                <template #item="{ element }">
                    <TaskCard :task="element" @edit="openModal(element)" @delete="deleteTask(element.id)"
                        @refresh="fetchTasks" @clone="cloneTask(element)" />
                </template>
            </draggable>

            <div v-if="tasks.length === 0"
                class="text-center bg-white dark:bg-gray-800 rounded-xl p-12 shadow-sm border border-gray-100 dark:border-gray-700 mt-8">
                <div class="inline-flex p-4 rounded-full bg-gray-50 dark:bg-gray-700 mb-4">
                    <LayoutDashboard :size="48" class="text-gray-300 dark:text-gray-500" />
                </div>
                <p class="text-gray-500 dark:text-gray-400 text-lg mb-4">No monitoring tasks running.</p>
                <button @click="openModal()"
                    class="text-blue-600 font-medium hover:underline flex items-center justify-center gap-1 mx-auto">
                    <Plus :size="16" /> Create your first task
                </button>
            </div>
        </div>

        <TaskModal v-if="showModal" :task="selectedTask" @close="closeModal" @save="saveTask" />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import draggable from 'vuedraggable'
import TaskCard from './components/TaskCard.vue'
import TaskModal from './components/TaskModal.vue'
import { Moon, Sun, Plus, LayoutDashboard } from 'lucide-vue-next'

const tasks = ref([])
const showModal = ref(false)
const selectedTask = ref(null)
const isDark = ref(false)
const isDragging = ref(false)

const API_URL = '/api'

const toggleDark = () => {
    isDark.value = !isDark.value
    if (isDark.value) {
        document.documentElement.classList.add('dark')
        localStorage.setItem('theme', 'dark')
    } else {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('theme', 'light')
    }
}

const onDragEnd = async () => {
    isDragging.value = false
    const orderedIds = tasks.value.map(t => t.id)
    try {
        await axios.put(`${API_URL}/tasks/reorder`, orderedIds)
    } catch (e) {
        console.error("Failed to reorder", e)
    }
}

const cloneTask = async (task) => {
    const newTask = {
        name: `${task.name} (Copy)`,
        login_id: task.login_id,
        password: task.password,
        chat_id: task.chat_id,
        target_semester_code: task.target_semester_code,
        interval: task.interval
    }
    await saveTask(newTask)
}

const fetchTasks = async () => {
    if (isDragging.value) return
    try {
        const res = await axios.get(`${API_URL}/tasks`)
        tasks.value = res.data.data
    } catch (e) {
        console.error(e)
    }
}

const openModal = (task = null) => {
    selectedTask.value = task ? { ...task } : null
    showModal.value = true
}

const closeModal = () => {
    showModal.value = false
    selectedTask.value = null
}

const saveTask = async (taskData) => {
    try {
        if (taskData.id) {
            await axios.put(`${API_URL}/tasks/${taskData.id}`, taskData)
        } else {
            await axios.post(`${API_URL}/tasks`, taskData)
        }
        fetchTasks()
        closeModal()
    } catch (e) {
        console.error(e)
        alert('Error saving task')
    }
}

const deleteTask = async (id) => {
    if (!confirm('Are you sure you want to delete this task?')) return
    try {
        await axios.delete(`${API_URL}/tasks/${id}`)
        fetchTasks()
    } catch (e) {
        console.error(e)
        alert('Error deleting task')
    }
}

onMounted(() => {
    fetchTasks()
    setInterval(fetchTasks, 3000)

    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
        if (savedTheme === 'dark') {
            isDark.value = true
            document.documentElement.classList.add('dark')
        }
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        isDark.value = true
        document.documentElement.classList.add('dark')
    }
})
</script>