from pathlib import Path

def hien_thi_cay_thu_muc(thu_muc_goc, clear_prefix=""):
    path = Path(thu_muc_goc)
    # Lấy danh sách file và thư mục con bên trong, sắp xếp theo tên
    items = sorted(list(path.iterdir()))
    
    for i, item in enumerate(items):
        # Kiểm tra xem đây có phải là phần tử cuối cùng trong thư mục hiện tại không
        is_last = (i == len(items) - 1)
        
        # Định dạng ký tự nhánh cây
        symbol = "└── " if is_last else "├── "
        print(f"{clear_prefix}{symbol}{item.name}")
        
        # Nếu là thư mục, tiếp tục đệ quy vào bên trong
        if item.is_dir():
            next_prefix = clear_prefix + ("    " if is_last else "│   ")
            hien_thi_cay_thu_muc(item, next_prefix)

if __name__ == "__main__":
    # '.' đại diện cho thư mục hiện tại đang đứng để chạy code
    thu_muc_hien_tai = "."
    print(f"Cấu trúc thư mục của: {Path(thu_muc_hien_tai).resolve().name}")
    hien_thi_cay_thu_muc(thu_muc_hien_tai)