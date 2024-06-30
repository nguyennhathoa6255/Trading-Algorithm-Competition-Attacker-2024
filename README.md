# Cuộc thi FinTech -  Attacker 2024 - Trading Algorithm<br>
### Đội thi: **Stack Overflow**

## CẬP NHẬT VÒNG CHUNG KẾT
### Sử dụng chiến lược đầu tư ngắn hạn:
![title-image](/image/chungket.png)
- Triển khai trên Streamlit: [Link](https://stack-overflow-attacker2024.streamlit.app/)

- Chiến lược giao dịch trên Trading View: [MACD with Magic Trend](https://in.tradingview.com/script/c3jUSRbK-Moving-Average-Convergence-Divergence-with-Magic-Trend/)
## VÒNG 2 - ALGORITHMIC ODYSSEY

## Tổng quan

### Lọc cổ phiếu và xây dựng thuật toán

- Truy cập nhánh 'report', vào thư mục Report và mở file Trading_Summary.ipynb đề xem kết quả sau khi dùng bộ lọc và mô phỏng thuật toán giao dịch trong 3 kì giao dịch có thời hạn mỗi kì 1 năm.

### Trực quan hóa dữ liệu từ các thuật toán
- Truy cập [link](https://stackoverflow-attacker2024.streamlit.app/) để xem biểu đồ trực quan.
- Nhóm sử dụng streamlit để trực quan hóa biến động giá trong suốt kì giao dịch của các mã cổ phiếu được chọn từ bộ lọc.
- Đồng thời vẽ các điểm mua/bán dựa theo tín hiệu của thuật toán do nhóm xây dựng.
- Hơn nữa còn có thông tin về phần trăm danh mục của các mã cố phiếu, hiệu suất theo ngày so với VN-INDEX khi sử dụng điểm mua/bán do thuật toán sinh ra.

![title-image](/image/vong2.png)
## Tổ chức dự án

- Lọc cổ phiếu: Main -> FilteringStock -> stock_filter_past.py
- Thuật toán đưa ra tín hiệu mua/bán: Main -> Algorithm -> alphas.py, calculation.py

```
├── config/                           : Cấu hình
├── Main/                             : Xây dựng thuật toán
│   └── Algorithm/                    : Xây dựng thuật toán giao dịch
│   │   ├── action.py                  
│   │   ├── alphas.py
│   │   ├── calculation.py
│   │   ├── weight.ipynb
│   │   └── weight.py
│   ├── Chart/                        : Kết quả các năm
│   ├── Class/                        : Tạo portfolio
│   ├── StockFiltering/               : Lọc cổ phiếu
│   ├── chart.py                      : Triển khai streamlit
│   └── main.py                       : Tính toán 
├── image/                            : Ảnh, chứng nhận                        
├── .gitignore                        
├── setup.py                          : Thiết lập
├── README.md                         : Báo cáo
└── requirements.txt                  : Package cần thiết

```

## Thành viên nhóm


#### Trần Nhàn (UEL) | Trịnh Thanh (UEL) | Khánh Huy (UEL) | Nhật Hoa (HUB) | Hoàng Quốc (HCMUS)
---

#### Kho lưu trữ gốc: [ORIGINAL REPOSITORY](https://github.com/jsyizdabet/Attacker-2024)

## Chứng nhận
![title-image](/image/chungnhan2.png)
![title-image](/image/chungnhan1.jpeg)
