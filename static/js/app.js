let token = localStorage.getItem('token');
let currentPage = 0;
const pageSize = 12;

$(function () {
    if (token) {
        showAdminPanel();
        loadImages();
    } else {
        showLoginPanel();
    }

    // 登录
    $('#login-btn').click(async function () {
        const password = $('#password').val();
        try {
            const resp = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({username: 'admin', password: password})
            });
            if (!resp.ok) {
                const err = await resp.json();
                $('#login-error').text(err.detail).show();
                return;
            }
            const data = await resp.json();
            token = data.access_token;
            localStorage.setItem('token', token);
            showAdminPanel();
            loadImages();
        } catch (e) {
            $('#login-error').text('网络错误').show();
        }
    });

    // 退出
    $('#logout-btn').click(function () {
        localStorage.removeItem('token');
        token = null;
        showLoginPanel();
        $('#image-list').empty();
    });

    // 上传
    $('#upload-form').submit(async function (e) {
        e.preventDefault();
        const fileInput = $('#file-input')[0];
        if (!fileInput.files.length) return;
        const file = fileInput.files[0];
        if (file.size > 10 * 1024 * 1024) {
            $('#upload-status').html('<span class="text-danger">文件大小不能超过 10MB</span>');
            return;
        }
        const formData = new FormData();
        formData.append('file', file);

        $('#upload-status').html('<span class="text-info">上传中...</span>');
        try {
            const resp = await fetch('/api/upload', {
                method: 'POST',
                headers: {'Authorization': `Bearer ${token}`},
                body: formData
            });
            if (!resp.ok) {
                const err = await resp.json();
                $('#upload-status').html(`<span class="text-danger">${err.detail}</span>`);
                return;
            }
            const data = await resp.json();
            $('#upload-status').html(`
                <span class="text-success">上传成功！</span>
                <button class="btn btn-sm btn-outline-info copy-markdown ms-2" data-markdown="${data.markdown}">复制 Markdown</button>
                <button class="btn btn-sm btn-outline-secondary copy-url ms-1" data-url="${data.url}">复制直链</button>
            `);
            fileInput.value = '';
            // 重新加载列表
            currentPage = 0;
            $('#image-list').empty();
            loadImages();
        } catch (e) {
            $('#upload-status').html('<span class="text-danger">上传失败</span>');
        }
    });

    // 加载更多
    $('#load-more-btn').click(function () {
        loadImages();
    });

    // 委托事件：复制链接
    $(document).on('click', '.copy-markdown', function () {
        copyToClipboard($(this).data('markdown'));
        $(this).text('已复制').addClass('btn-success').removeClass('btn-outline-info');
        setTimeout(() => {
            $(this).text('复制 Markdown').removeClass('btn-success').addClass('btn-outline-info');
        }, 2000);
    });

    // 下载原图
    $(document).on('click', '.download-btn', function (e) {
        e.preventDefault();
        const url = $(this).data('url');
        const filename = $(this).data('filename');
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });

    $(document).on('click', '.copy-url', function () {
        copyToClipboard($(this).data('url'));
        $(this).text('已复制').addClass('btn-success').removeClass('btn-outline-secondary');
        setTimeout(() => {
            $(this).text('复制直链').removeClass('btn-success').addClass('btn-outline-secondary');
        }, 2000);
    });

    // 删除图片
    $(document).on('click', '.delete-btn', async function () {
        if (!confirm('确认删除此图片？')) return;
        const id = $(this).data('id');
        const card = $(this).closest('.col');
        try {
            const resp = await fetch(`/api/images/${id}`, {
                method: 'DELETE',
                headers: {'Authorization': `Bearer ${token}`}
            });
            if (resp.ok) {
                card.fadeOut(300, function () {
                    $(this).remove();
                });
            } else {
                alert('删除失败');
            }
        } catch (e) {
            alert('网络错误');
        }
    });
});

function showLoginPanel() {
    $('#login-panel').show();
    $('#admin-panel').hide();
    $('#password').val('');
}

function showAdminPanel() {
    $('#login-panel').hide();
    $('#admin-panel').show();
}

async function loadImages() {
    const resp = await fetch(`/api/images?skip=${currentPage * pageSize}&limit=${pageSize}`, {
        headers: {'Authorization': `Bearer ${token}`}
    });
    if (!resp.ok) {
        // Token 可能过期
        localStorage.removeItem('token');
        token = null;
        showLoginPanel();
        return;
    }
    const images = await resp.json();
    if (images.length === 0) {
        $('#load-more-btn').hide();
        return;
    }
    for (const img of images) {
        // 格式化文件大小
        function formatSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        const date = new Date(img.upload_time).toLocaleString('zh-CN');
        const rowHtml = `
        <tr>
            <td><a href="${img.thumb_url}" target="_blank"><img src="${img.thumb_url}" class="img-thumbnail" style="max-width:100px; max-height:80px;" alt="${img.original_name}" loading="lazy"></a></td>
            <td title="${img.original_name}">${img.original_name}</td>
            <td>${formatSize(img.size)}</td>
            <td>${date}</td>
            <td style="white-space: nowrap;">
                <button class="btn btn-sm btn-outline-primary copy-url" data-url="${img.url}">复制URL</button>
                <button class="btn btn-sm btn-outline-success copy-markdown ms-1" data-markdown="![${img.original_name}](${window.location.origin}${img.url})">复制Markdown</button>
                <button class="btn btn-sm btn-outline-secondary download-btn ms-1" data-url="${window.location.origin}${img.url}" data-filename="${img.original_name}">下载</button>
                <button class="btn btn-sm btn-outline-danger delete-btn ms-1" data-id="${img.id}">删除</button>
            </td>
        </tr>`;
        $('#image-list').append(rowHtml);
        // $('#image-list').append(cardHtml);
    }
    currentPage++;
    if (images.length === pageSize) {
        $('#load-more-btn').show();
    } else {
        $('#load-more-btn').hide();
    }
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
}