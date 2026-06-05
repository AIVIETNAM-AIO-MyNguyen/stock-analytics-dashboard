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
            # Đảm bảo giữ nguyên cấu hình group_by cũ để tránh lỗi cấu trúc bảng
            stock_data = yf.download(ticker, period="1mo")
        
        if not stock_data.empty:
            # Ép mảng dữ liệu về dạng phẳng đơn giản để loại bỏ lỗi đa tầng của yfinance
            df = stock_data.copy()
            
            # Lấy giá đóng cửa ngày gần nhất và ngày trước đó một cách an toàn
            try:
                price_today = float(df['Close'].iloc[-1])
                if len(df) > 1:
                    price_yesterday = float(df['Close'].iloc[-2])
                    delta_price = price_today - price_yesterday
                else:
                    delta_price = 0.0
                volume_today = int(df['Volume'].iloc[-1])
            except Exception:
                # Phương án dự phòng nếu cấu trúc bảng bị thay đổi theo phiên
                price_today = float(df['Close'].values[-1])
                delta_price = 0.0
                volume_today = int(df['Volume'].values[-1])

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
                ax.plot(df.index, df['Close'], label="Close Price", color="#1f77b4", linewidth=2)
                
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
