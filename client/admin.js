const CONFIG = {
    API_BASE_URL: window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' 
        ? "http://127.0.0.1:8000/api" 
        : "/api"
};

let cropChart = null;
let regionChart = null;

// Kiểm tra quyền Admin khi vào trang
function checkAuth() {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
        window.location.href = 'index.html';
        return null;
    }
    const user = JSON.parse(userStr);
    if (user.role !== 'admin') {
        alert('Bạn không có quyền truy cập trang này!');
        window.location.href = 'index.html';
        return null;
    }
    return user;
}

const currentUser = checkAuth();

if (currentUser) {
    document.getElementById('admin-info').innerText = `Chào, ${currentUser.full_name || 'Quản trị viên'}`;
    loadStats();
    loadUsers();
    loadTrends();
    initMobileMenu();
}

function initMobileMenu() {
    const btn = document.getElementById('mobile-menu-btn');
    const closeBtn = document.getElementById('close-sidebar');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    btn.addEventListener('click', () => {
        sidebar.classList.remove('-translate-x-full');
        overlay.classList.remove('hidden');
    });

    const close = () => {
        sidebar.classList.add('-translate-x-full');
        overlay.classList.add('hidden');
    };

    closeBtn.addEventListener('click', close);
    overlay.addEventListener('click', close);
}

async function loadStats() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/admin/stats`, {
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        const data = await response.json();
        
        document.getElementById('stat-total-users').innerText = data.total_users;
        document.getElementById('stat-farmers').innerText = data.farmers;
        document.getElementById('stat-admins').innerText = data.admins;
        document.getElementById('kb-status').innerText = data.kb_status;
        
        if (data.kb_status === 'Ready') {
            document.getElementById('kb-status').classList.add('text-green-600');
        }

        // Vẽ biểu đồ
        renderCharts(data.crop_distribution, data.region_distribution);
    } catch (error) {
        console.error('Lỗi tải thống kê:', error);
    }
}

async function loadUsers() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/admin/users`, {
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        const users = await response.json();
        
        const tbody = document.getElementById('user-table-body');
        tbody.innerHTML = users.map(u => `
            <tr class="border-t border-slate-100 hover:bg-slate-50 transition-colors">
                <td class="py-4 px-4 text-sm text-slate-700">${u.email}</td>
                <td class="py-4 px-4">
                    <span class="px-3 py-1 text-[10px] font-bold rounded-full tracking-wider ${u.role === 'admin' ? 'bg-orange-100 text-orange-600' : 'bg-green-100 text-green-600'}">
                        ${u.role.toUpperCase()}
                    </span>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Lỗi tải danh sách người dùng:', error);
    }
}

document.getElementById('btn-reingest').addEventListener('click', async () => {
    if (!confirm('Bạn có chắc chắn muốn nạp lại toàn bộ tri thức không? Việc này có thể mất vài phút.')) return;
    
    const btn = document.getElementById('btn-reingest');
    btn.disabled = true;
    btn.innerText = '⌛ Đang xử lý...';
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/admin/ingest`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        const data = await response.json();
        alert(data.message);
    } catch (error) {
        alert('Lỗi kích hoạt nạp tri thức');
    } finally {
        btn.disabled = false;
        btn.innerText = '🔄 Cập nhật tri thức mới';
    }
});

// --- QUẢN LÝ FILE ---

if (currentUser) {
    loadFiles();
}

async function loadFiles() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/admin/files`, {
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        const files = await response.json();
        
        const fileList = document.getElementById('file-list');
        if (files.length === 0) {
            fileList.innerHTML = '<p class="text-xs text-slate-400 italic">Chưa có tài liệu nào.</p>';
            return;
        }
        
        fileList.innerHTML = files.map(f => `
            <div class="flex justify-between items-center p-2 bg-slate-50 rounded hover:bg-slate-100 transition-colors">
                <div class="flex flex-col">
                    <span class="text-sm font-medium text-slate-700 truncate max-w-[200px]" title="${f.name}">${f.name}</span>
                    <span class="text-[10px] text-slate-400">${(f.size / 1024 / 1024).toFixed(2)} MB</span>
                </div>
                <button onclick="deleteFile('${f.name}')" class="text-slate-400 hover:text-red-500 transition-colors p-1">
                    🗑️
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Lỗi tải danh sách file:', error);
    }
}

// Xử lý chọn file
document.getElementById('pdf-upload').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        document.getElementById('upload-filename').innerText = `Đang chọn: ${file.name}`;
        document.getElementById('btn-upload').classList.remove('hidden');
    }
});

// Xử lý upload
document.getElementById('btn-upload').addEventListener('click', async () => {
    const fileInput = document.getElementById('pdf-upload');
    const file = fileInput.files[0];
    if (!file) return;

    const btn = document.getElementById('btn-upload');
    btn.disabled = true;
    btn.innerText = '⌛ Đang tải lên...';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/admin/upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${currentUser.token}` },
            body: formData
        });
        const data = await response.json();
        if (response.ok) {
            alert('Tải lên thành công!');
            fileInput.value = '';
            document.getElementById('upload-filename').innerText = '';
            btn.classList.add('hidden');
            loadFiles();
        } else {
            alert('Lỗi: ' + data.detail);
        }
    } catch (error) {
        alert('Lỗi kết nối máy chủ khi upload');
    } finally {
        btn.disabled = false;
        btn.innerText = '⬆️ Bắt đầu tải lên';
    }
});

async function deleteFile(filename) {
    if (!confirm(`Bạn có chắc muốn xóa file "${filename}"?`)) return;

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/admin/files/${filename}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        if (response.ok) {
            loadFiles();
        } else {
            const data = await response.json();
            alert('Lỗi: ' + data.detail);
        }
    } catch (error) {
        alert('Lỗi khi xóa file');
    }
}

async function loadTrends() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/admin/trends`, {
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        const trends = await response.json();
        
        const container = document.getElementById('trends-list');
        if (trends.length === 0) {
            container.innerHTML = '<p class="text-sm text-slate-400 italic">Chưa có dữ liệu hội thoại.</p>';
            return;
        }

        const maxCount = Math.max(...trends.map(t => t.count));
        
        container.innerHTML = trends.map(t => `
            <div>
                <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium text-slate-700">${t.topic}</span>
                    <span class="text-slate-400">${t.count} lượt hỏi</span>
                </div>
                <div class="w-full bg-slate-100 rounded-full h-2">
                    <div class="bg-blue-500 h-2 rounded-full" style="width: ${(t.count / maxCount * 100)}%"></div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Lỗi tải xu hướng:', error);
    }
}

function renderCharts(cropData, regionData) {
    // 1. Biểu đồ Cơ cấu cây trồng (Pie Chart)
    const cropCtx = document.getElementById('cropChart').getContext('2d');
    if (cropChart) cropChart.destroy();
    
    cropChart = new Chart(cropCtx, {
        type: 'doughnut',
        data: {
            labels: cropData.map(d => d.label),
            datasets: [{
                data: cropData.map(d => d.value),
                backgroundColor: ['#10b981', '#f59e0b', '#3b82f6', '#ec4899', '#8b5cf6'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, padding: 20 } }
            },
            cutout: '70%'
        }
    });

    // 2. Biểu đồ Phân bố vùng trồng (Bar Chart)
    const regionCtx = document.getElementById('regionChart').getContext('2d');
    if (regionChart) regionChart.destroy();

    regionChart = new Chart(regionCtx, {
        type: 'bar',
        data: {
            labels: regionData.map(d => d.label.split(' - ')[0]), // Lấy tên ngắn
            datasets: [{
                label: 'Lượt hoạt động',
                data: regionData.map(d => d.value),
                backgroundColor: '#3b82f6',
                borderRadius: 8,
                barThickness: 30
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } },
                x: { grid: { display: false } }
            }
        }
    });
}
