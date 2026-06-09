"""
Dashboard Streamlit untuk Analisis Trend Saham Indonesia
"""

import streamlit as st
import pandas as pd
import numpy as np
from src.fetcher import SahamFetcher
from src.analyzer import SahamAnalyzer
from src.visualizer import SahamVisualizer
from src.predictor import TrendPredictor
import warnings

warnings.filterwarnings('ignore')

# Configure page
st.set_page_config(
    page_title="Analisis Trend Saham Indonesia",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = SahamAnalyzer()
if 'fetcher' not in st.session_state:
    st.session_state.fetcher = SahamFetcher()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = SahamVisualizer()
if 'predictor' not in st.session_state:
    st.session_state.predictor = TrendPredictor()

# Title
st.title("📈 Analisis Trend Kepemilikan Saham Indonesia")
st.markdown("*Dashboard untuk analisis fundamental dan teknikal saham BEI*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    page = st.radio("Pilih Menu:", 
        ["Dashboard Utama", "Analisis Detail", "Perbandingan Saham", "Prediksi", "Portfolio"])
    
    st.divider()
    
    st.subheader("Data Source")
    st.info("Data diambil dari Yahoo Finance dengan suffix .JK (Jakarta)")

# Main content
if page == "Dashboard Utama":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🔍 Cari Saham")
        stock_code = st.text_input("Masukkan kode saham (misal: BBCA):", value="BBCA").upper()
    
    with col2:
        st.subheader("📅 Periode")
        period = st.selectbox("Pilih periode:", 
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3)
    
    with col3:
        st.subheader("📊 Interval")
        interval = st.selectbox("Pilih interval:", 
            ["1d", "1wk", "1mo"],
            index=0)
    
    if st.button("📥 Ambil Data", type="primary"):
        with st.spinner(f"Mengambil data {stock_code}..."):
            analysis = st.session_state.analyzer.analyze_trend(stock_code, period=period)
            
            if analysis:
                st.session_state.analysis = analysis
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Harga Terakhir", f"Rp {analysis['last_price']:,.0f}")
                
                with col2:
                    st.metric("Return Harian", f"{analysis['change']:.2f}%",
                             delta_color="off" if analysis['change'] >= 0 else "inverse")
                
                with col3:
                    st.metric("Return Kumulatif", f"{analysis['cumulative_return']:.2f}%")
                
                with col4:
                    recommendation = analysis['trend_recommendation']
                    color = "🟢" if recommendation in ["STRONG BUY", "BUY"] else \
                           "🔴" if recommendation in ["STRONG SELL", "SELL"] else "🟡"
                    st.metric("Rekomendasi", f"{color} {recommendation}")
                
                st.divider()
                
                # Charts
                tab1, tab2, tab3, tab4 = st.tabs(["📈 Harga", "📊 Volume", "RSI", "Bollinger Bands"])
                
                with tab1:
                    fig = st.session_state.visualizer.plot_price_trend(analysis['data'], stock_code)
                    st.pyplot(fig)
                
                with tab2:
                    fig = st.session_state.visualizer.plot_volume(analysis['data'], stock_code)
                    st.pyplot(fig)
                
                with tab3:
                    if 'RSI' in analysis['data'].columns:
                        fig = st.session_state.visualizer.plot_rsi(analysis['data'], stock_code)
                        st.pyplot(fig)
                    else:
                        st.warning("RSI data tidak tersedia")
                
                with tab4:
                    if 'BB_Upper' in analysis['data'].columns:
                        fig = st.session_state.visualizer.plot_bollinger_bands(analysis['data'], stock_code)
                        st.pyplot(fig)
                    else:
                        st.warning("Bollinger Bands data tidak tersedia")
                
                # Technical indicators
                st.subheader("📊 Indikator Teknikal")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    rsi_val = analysis['rsi']
                    if rsi_val:
                        status = "Overbought" if rsi_val > 70 else "Oversold" if rsi_val < 30 else "Normal"
                        st.metric("RSI (14)", f"{rsi_val:.2f}", status)
                
                with col2:
                    st.metric("Volatilitas", f"{analysis['avg_volatility']:.2f}%")
                
                with col3:
                    st.metric("Jumlah Data", len(analysis['data']))
            else:
                st.error(f"Tidak bisa mengambil data untuk {stock_code}")

elif page == "Analisis Detail":
    st.subheader("🔬 Analisis Detail Saham")
    
    col1, col2 = st.columns(2)
    
    with col1:
        stock_code = st.text_input("Kode saham:", value="BBCA", key="detail_stock").upper()
    
    with col2:
        period = st.selectbox("Periode:", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], 
                            key="detail_period")
    
    if st.button("Analisis", key="detail_btn"):
        with st.spinner("Menganalisis..."):
            analysis = st.session_state.analyzer.analyze_trend(stock_code, period=period)
            
            if analysis:
                # Info saham
                info = st.session_state.fetcher.get_stock_info(stock_code)
                if info:
                    st.subheader(f"ℹ️ {info['name']}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Sektor:** {info['sector']}")
                    with col2:
                        st.write(f"**Industri:** {info['industry']}")
                    with col3:
                        st.write(f"**Market Cap:** {info['market_cap']}")
                
                st.divider()
                
                # Detailed statistics
                st.subheader("📋 Statistik Detail")
                
                data = analysis['data']
                stats_df = pd.DataFrame({
                    'Metrik': [
                        'Harga Tertinggi',
                        'Harga Terendah',
                        'Harga Rata-rata',
                        'Harga Penutupan Terakhir',
                        'Volume Rata-rata',
                        'Volatilitas (Std Dev)',
                        'Return Min',
                        'Return Max',
                        'Return Rata-rata'
                    ],
                    'Nilai': [
                        f"Rp {data['High'].max():,.0f}",
                        f"Rp {data['Low'].min():,.0f}",
                        f"Rp {data['Close'].mean():,.0f}",
                        f"Rp {analysis['last_price']:,.0f}",
                        f"{data['Volume'].mean():,.0f}",
                        f"{analysis['avg_volatility']:.2f}%",
                        f"{data['Daily_Return'].min():.2f}%",
                        f"{data['Daily_Return'].max():.2f}%",
                        f"{data['Daily_Return'].mean():.2f}%"
                    ]
                })
                
                st.dataframe(stats_df, use_container_width=True)
                
                # Distribution analysis
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Distribusi Return")
                    fig = st.session_state.visualizer.plot_returns_distribution(data, stock_code)
                    st.pyplot(fig)
                
                with col2:
                    st.subheader("📈 Data Preview")
                    st.dataframe(data.tail(10), use_container_width=True)

elif page == "Perbandingan Saham":
    st.subheader("⚖️ Perbandingan Saham")
    
    stock_list = st.multiselect("Pilih saham untuk dibandingkan:",
        list(SahamFetcher.POPULAR_STOCKS.keys()),
        default=['BBCA', 'BBRI', 'BMRI'])
    
    if st.button("Bandingkan", key="compare_btn"):
        with st.spinner("Membandingkan..."):
            comparison = st.session_state.analyzer.compare_stocks(stock_list, period='1y')
            
            st.subheader("📊 Hasil Perbandingan")
            st.dataframe(comparison, use_container_width=True)
            
            # Interactive chart
            fig = st.session_state.visualizer.plot_interactive_comparison(comparison)
            st.plotly_chart(fig, use_container_width=True)
            
            # Download CSV
            csv = comparison.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="perbandingan_saham.csv",
                mime="text/csv"
            )

elif page == "Prediksi":
    st.subheader("🔮 Prediksi Trend Saham")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stock_code = st.text_input("Kode saham:", value="BBCA", key="pred_stock").upper()
    
    with col2:
        periods = st.slider("Periode prediksi (hari):", 1, 30, 5)
    
    with col3:
        method = st.selectbox("Metode prediksi:",
            ["Linear Regression", "Random Forest", "Exponential Smoothing"])
    
    if st.button("Prediksi", key="pred_btn"):
        with st.spinner("Melakukan prediksi..."):
            data = st.session_state.fetcher.fetch_stock_data(stock_code, period='1y')
            
            if data is not None:
                predictor = st.session_state.predictor
                
                # Ambil prediksi
                if method == "Linear Regression":
                    predictions = predictor.predict_linear(data, periods=periods)
                elif method == "Random Forest":
                    predictions = predictor.predict_random_forest(data, periods=periods)
                else:
                    predictions = predictor.predict_exponential_smoothing(data, periods=periods)
                
                if predictions is not None:
                    # Confidence
                    confidence = predictor.calculate_prediction_confidence(data, predictions, 
                                                                          method=method.lower().replace(" ", "_"))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Confidence Score", f"{confidence:.1f}%")
                    with col2:
                        st.metric("Metode", method)
                    
                    # Prediction table
                    pred_df = pd.DataFrame({
                        'Hari ke': range(1, periods + 1),
                        'Prediksi Harga': predictions.round(0)
                    })
                    
                    st.subheader("📊 Hasil Prediksi")
                    st.dataframe(pred_df, use_container_width=True)
                    
                    # Chart
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(12, 6))
                    
                    last_price = data['Close'].iloc[-1]
                    dates = pd.date_range(start=data['Date'].iloc[-1], periods=periods+1, freq='D')[1:]
                    
                    ax.plot(data['Date'].tail(50), data['Close'].tail(50), label='Harga Historis', linewidth=2)
                    ax.plot(dates, predictions, label=f'Prediksi ({method})', linewidth=2, linestyle='--', color='red')
                    ax.scatter(dates, predictions, color='red', s=50, zorder=5)
                    
                    ax.set_title(f'Prediksi Harga {stock_code}', fontsize=14, fontweight='bold')
                    ax.set_xlabel('Tanggal')
                    ax.set_ylabel('Harga (IDR)')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    st.pyplot(fig)
            else:
                st.error(f"Tidak bisa mengambil data untuk {stock_code}")

elif page == "Portfolio":
    st.subheader("💼 Analisis Portfolio")
    
    st.info("Fitur untuk menganalisis portfolio saham Anda")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Input Portfolio")
        
        portfolio_data = []
        num_stocks = st.number_input("Jumlah saham:", min_value=1, max_value=10, value=3)
        
        for i in range(num_stocks):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                code = st.text_input(f"Kode saham {i+1}:", value="BBCA", key=f"port_code_{i}").upper()
            with col_b:
                qty = st.number_input(f"Lot {i+1}:", value=1, key=f"port_qty_{i}")
            with col_c:
                price = st.number_input(f"Harga {i+1}:", value=10000, key=f"port_price_{i}")
            
            if code:
                portfolio_data.append({
                    'Saham': code,
                    'Lot': int(qty),
                    'Harga Beli': float(price),
                    'Nilai': int(qty) * float(price)
                })
        
        portfolio_df = pd.DataFrame(portfolio_data)
    
    with col2:
        st.subheader("📊 Ringkasan Portfolio")
        if not portfolio_df.empty:
            total_value = portfolio_df['Nilai'].sum()
            st.metric("Total Nilai", f"Rp {total_value:,.0f}")
            
            # Pie chart
            import plotly.express as px
            fig = px.pie(portfolio_df, values='Nilai', names='Saham', 
                        title='Alokasi Portfolio')
            st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    <p>Dashboard Analisis Trend Saham Indonesia | Data: Yahoo Finance</p>
    <p>⚠️ Disclaimer: Program ini hanya untuk tujuan edukasi. Bukan merupakan saran investasi profesional.</p>
    </div>
""", unsafe_allow_html=True)
