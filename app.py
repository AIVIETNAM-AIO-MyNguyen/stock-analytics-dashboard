import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

# Cấu hình trang hiển thị rộng rãi chuẩn Dashboard doanh nghiệp
st.set_page_config(page_title="Advanced Stock Analytics Dashboard", page_icon="📈", layout="wide")

# Tiêu đề chính trên màn hình lớn
st.title("📈 Advanced Stock Analytics Dashboard")
st.markdown("---")

# Danh sách mã cổ phiếu có sẵn
TICKER_LIST = ["TSLA", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "NFLX", "NKE", "AMD"]

# 1. Giao diện Sidebar: Đẩy phần chọn mã sang bên trái
st.sidebar.header("⚙️ BẢNG ĐIỀU KHIỂN")
selected_tickers = st.sidebar.multiselect(
    "Chọn các mã cổ phiếu:", 
    options=TICKER_LIST, 
    default=["TSLA"]
)

st.sidebar.markdown("""
---
*Hướng dẫn: Bạn có thể chọn cùng lúc nhiều mã để so sánh và theo dõi.*
""")

# Hiển thị dữ liệu trên khu vực chính
if selected_tickers:
    for ticker in selected_tickers:
        st.markdown(f"## 📊 Phân tích mã cổ phiếu: **{ticker}**")
        
        with st.spinner(f'Đang tải dữ liệu cho {ticker}...'):
            # Tải dữ liệu 1 tháng gần nhất
            df = yf.download(ticker, period="1mo")
        
        if not df.empty:
            # Xử lý bóc tách mảng giá đóng cửa (Close) và Khối lượng (Volume) an toàn
            try:
                # Trường hợp yfinance trả về bảng dữ liệu đa tầng (Multi-index)
                if isinstance(df.columns, tuple) or hasattr(df.columns, 'levels'):
                    close_series = df.xs('Close', axis=1, level=0)[ticker]
                    volume_series = df.xs('Volume', axis=1, level=0)[ticker]
                else:
                    # Trường hợp bảng phẳng thông thường
                    close_series = df['Close']
                    volume_series = df['Volume']
            except Exception:
                # Phương án dự phòng cuối cùng bóc tách theo vị trí cột gốc nếu cấu trúc biến động
                close_series = df.iloc[:, 3]
                volume_series = df.iloc[:, 5]

            # Ép về mảng phẳng 1 chiều để xử lý trích xuất số liệu chính xác
            close_values = close_series.values.flatten()
            volume_values = volume_series.values.flatten()
            
            price_today = float(close_values[-1])
            if len(close_values) > 1:
                price_yesterday = float(close_values[-2])
                delta_price = price_today - price_yesterday
            else:
                delta_price = 0.0
            volume_today = int(volume_values[-1])

            # 2. Thẻ KPI (Metrics): Hiển thị giá và mũi tên xanh/đỏ tăng giảm
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label=f"Giá đóng cửa gần nhất ({ticker})", 
                    value=f"${price_today:,.2f}", 
                    delta=f"${delta_price:,.2f}"
                )
            with col2:
                st.metric(
                    label="Khối lượng giao dịch gần nhất", 
                    value=f"{volume_today:,} cp"
                )
            
            st.write("") # Tạo khoảng cách dòng nhỏ

            # 3. Tính năng Tabs: Gom Biểu đồ và Bảng dữ liệu để giao diện không bị dài
            tab1, tab2 = st.tabs(["📉 Biểu đồ xu hướng (Matplotlib)", "📋 Bảng dữ liệu chi tiết"])
            
            with tab1:
                # Vẽ biểu đồ bằng Matplotlib chi tiết chuẩn ảnh mong muốn
                fig, ax = plt.subplots(figsize=(10, 4.5))
                ax.plot(df.index, close_values, label="Close Price", color="#1f77b4", linewidth=2)
                
                # Định dạng tiêu đề và nhãn trục
                ax.set_title(f"{ticker} Closing Prices (Last 1 Month)", fontsize=14, pad=10)
                ax.set_xlabel("Date", fontsize=11)
                ax.set_ylabel("Price (USD)", fontsize=11)
                ax.legend(loc="upper right")
                ax.grid(True, linestyle="--", alpha=0.5)
                
                # Đưa lên tab 1
                st.pyplot(fig)
                plt.close(fig)
                
            with tab2:
                # Đưa bảng dữ liệu hiển thị lên tab 2
                st.dataframe(df.sort_index(ascending=False), use_container_width=True)
                
            st.markdown("---") # Kẻ đường phân cách nếu chọn nhiều mã
        else:
            st.error(f"❌ Không tìm thấy dữ liệu cho mã '{ticker}'")
else:
    st.info("💡 Vui lòng chọn ít nhất một mã cổ phiếu ở thanh Sidebar bên trái để hiển thị dữ liệu!")
