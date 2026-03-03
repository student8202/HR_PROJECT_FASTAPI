const Auth = {
    // --- HÀM ĐĂNG NHẬP (Chuyển từ login.html sang đây) ---
    doLogin: async function () {
        const username = $('#user').val();
        const password = $('#pass').val();

        if (!username || !password) {
            alert("Vui lòng nhập tài khoản và mật khẩu");
            return;
        }

        try {
            const res = await fetch('auth/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();

            if (data.status === "success") {
                // Lưu mọi thứ vào trình duyệt
                localStorage.setItem('userName', data.user.name);
                localStorage.setItem('userPerms', data.user.perms);
                // Chuyển hướng
                window.location.href = '/';
            } else {
                // Hiển thị lỗi từ server
                $('#error-msg').text(data.message).removeClass('d-none');
            }
        } catch (error) {
            console.error("Login Error:", error);
            $('#error-msg').text("Lỗi kết nối hệ thống!").removeClass('d-none');
        }
    },

    // --- HÀM LẤY QUYỀN ---
    getPerms: () => (localStorage.getItem('userPerms') || "").split(','),

    // --- KIỂM TRA QUYỀN ---
    has: (p) => Auth.getPerms().includes(p),

    // --- ĐĂNG XUẤT ---
    logout: () => {
        fetch('auth/api/logout')
            .catch(err => console.error("Logout Error:", err))
            .finally(() => {
                // KHÔNG dùng localStorage.clear();

                // Chỉ xóa thông tin đăng nhập
                localStorage.removeItem('userPerms');
                localStorage.removeItem('userName');

                // Giữ nguyên localStorage.getItem('appLang')

                window.location.replace('auth/login');
            });
    }
};

// async function doLogin() {
//     const username = $('#user').val();
//     const password = $('#pass').val();

//     const res = await fetch('/api/login', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ username, password })
//     });
//     const data = await res.json();

//     if (data.status === "success") {
//         // --- THÊM DÒNG NÀY ---
//         localStorage.setItem('userName', data.user.name);
//         // ---------------------
//         localStorage.setItem('userPerms', data.user.perms);
//         window.location.href = '/';
//     } else {
//         $('#error-msg').text(data.message).removeClass('d-none');
//     }
// }