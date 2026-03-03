# -*- coding: utf-8 -*-
"""
地学大数据基础 - 在线实验平台
Streamlit 教学应用：学生可在线进行气象、DEM、缺失值、归一化、降水、网格等实验
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

st.set_page_config(
    page_title="地学大数据基础 - 在线实验",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式：简洁教学风格
st.markdown("""
<style>
    .main-header { font-size: 1.8rem; color: #1e3a5f; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #4a6fa5; margin-bottom: 1rem; }
    .exp-card { padding: 1rem; border-radius: 8px; background: #f0f4f8; margin: 0.5rem 0; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
</style>
""", unsafe_allow_html=True)


def main():
    st.markdown('<p class="main-header">🌍 地学大数据基础 · 在线实验平台</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">选择左侧实验模块，在线完成数据处理与可视化。</p>', unsafe_allow_html=True)

    experiment = st.sidebar.radio(
        "**选择实验**",
        [
            "📊 实验一：气温与气象数据分析",
            "⛰️ 实验二：DEM 高程网格与地形",
            "❓ 实验三：缺失值处理",
            "📐 实验四：数据归一化（Min-Max）",
            "🌧️ 实验五：降水量统计",
            "🗺️ 实验六：经纬度网格（meshgrid）",
        ],
        index=0,
    )

    if "气温" in experiment:
        page_weather()
    elif "DEM" in experiment:
        page_dem()
    elif "缺失值" in experiment:
        page_missing()
    elif "归一化" in experiment:
        page_normalize()
    elif "降水" in experiment:
        page_precipitation()
    else:
        page_meshgrid()


def page_weather():
    """实验一：气温与气象数据分析"""
    st.header("实验一：气温与气象数据分析")
    st.markdown("模拟多站点气温数据，进行统计与可视化；支持上传 CSV 或使用示例数据。")

    use_sample = st.radio("数据来源", ["使用示例数据（5 站点 × 30 天）", "上传 CSV 文件"], horizontal=True)

    if use_sample == "使用示例数据（5 站点 × 30 天）":
        np.random.seed(123)
        base_temps = np.linspace(15, 25, 30)
        noise = np.random.randn(5, 30) * 3
        temps = base_temps + noise
        stations = [f"站点{i+1}" for i in range(5)]
        days = list(range(1, 31))
        df = pd.DataFrame(temps.T, columns=stations)
        df.insert(0, "日期", days)
        df_long = df.melt(id_vars=["日期"], var_name="站点", value_name="气温(℃)")
    else:
        uploaded = st.file_uploader("上传 CSV（需含日期/站点/气温等列）", type=["csv"])
        if uploaded is None:
            st.info("请上传 CSV 文件，或先使用示例数据。")
            return
        df = pd.read_csv(uploaded)
        st.subheader("数据预览")
        st.dataframe(df.head(10), use_container_width=True)
        col_options = list(df.columns)
        date_col = st.selectbox("日期列", col_options, index=min(0, len(col_options) - 1))
        station_col = st.selectbox("站点列", col_options, index=min(1, len(col_options) - 1))
        temp_col = st.selectbox("气温列", col_options, index=min(2, len(col_options) - 1))
        df_long = df.rename(columns={date_col: "日期", station_col: "站点", temp_col: "气温(℃)"})[["日期", "站点", "气温(℃)"]]

    st.subheader("统计结果")
    if "气温(℃)" in df_long.columns:
        stats = df_long.groupby("站点")["气温(℃)"].agg(["mean", "std", "min", "max"]).round(2)
        stats.columns = ["平均气温(℃)", "标准差", "最低温(℃)", "最高温(℃)"]
        st.dataframe(stats, use_container_width=True)
        st.write(f"**全区域最高温：** {df_long['气温(℃)'].max():.2f} ℃")
        st.write(f"**全区域最低温：** {df_long['气温(℃)'].min():.2f} ℃")

    st.subheader("气温变化曲线")
    fig = px.line(df_long, x="日期", y="气温(℃)", color="站点", title="各站点气温时序")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("箱线图（分布对比）")
    fig2 = px.box(df_long, x="站点", y="气温(℃)", title="各站点气温分布")
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)


def page_dem():
    """实验二：DEM 高程网格与地形"""
    st.header("实验二：DEM 高程网格与地形")
    st.markdown("生成模拟 DEM（数字高程模型）网格，查看高程统计并可视化地形曲面。")

    n = st.slider("网格大小 (n×n)", 5, 25, 10)
    seed = st.number_input("随机种子", 0, 99999, 42)
    np.random.seed(seed)
    x = np.linspace(-2, 2, n)
    y = np.linspace(-2, 2, n)
    X, Y = np.meshgrid(x, y)
    Z = 100 - X**2 - Y**2 + np.random.rand(n, n) * 5

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("最高点高程 (m)", f"{Z.max():.1f}")
    with col2:
        st.metric("最低点高程 (m)", f"{Z.min():.1f}")
    with col3:
        st.metric("平均高程 (m)", f"{Z.mean():.1f}")

    st.subheader("高程矩阵（部分）")
    st.dataframe(pd.DataFrame(Z).iloc[:6, :6].round(1), use_container_width=True)

    st.subheader("3D 地形曲面")
    fig = go.Figure(data=[go.Surface(z=Z, x=x, y=y, colorscale="Terrain")])
    fig.update_layout(
        title="DEM 地形曲面",
        scene=dict(
            xaxis_title="X", yaxis_title="Y", zaxis_title="高程 (m)",
            aspectmode="data"
        ),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("等高线图")
    fig2 = go.Figure(data=go.Contour(z=Z, x=x, y=y, colorscale="Viridis"))
    fig2.update_layout(title="等高线", xaxis_title="X", yaxis_title="Y", height=400)
    st.plotly_chart(fig2, use_container_width=True)


def page_missing():
    """实验三：缺失值处理"""
    st.header("实验三：缺失值处理")
    st.markdown("地学数据常用 **-9999** 或 **NaN** 表示缺失。练习用布尔索引过滤缺失值，或用均值填充。")

    st.subheader("示例数据（含缺失）")
    raw = np.array([12.5, 15.3, -9999, 18.2, -9999, 20.1, 16.8])
    missing_val = st.number_input("缺失值标记（整数）", value=-9999)
    data = raw.copy()

    col1, col2 = st.columns(2)
    with col1:
        st.write("原始数据（含缺失）")
        st.write(pd.DataFrame({"值": data}))
    valid_mask = data != missing_val
    valid_data = data[valid_mask]
    with col2:
        st.write("过滤缺失后的有效数据")
        st.write(pd.DataFrame({"值": valid_data}))

    st.write("**有效数据均值：**", round(valid_data.mean(), 2))

    st.subheader("用 NaN 表示缺失（nanmean 忽略 NaN）")
    data_nan = np.array([12.5, 15.3, np.nan, 18.2, np.nan, 20.1, 16.8], dtype=float)
    filled_mean = np.nanmean(data_nan)
    st.write("含 NaN 的数组：", data_nan)
    st.write("**nanmean（忽略 NaN）：**", round(filled_mean, 2))

    fill_choice = st.radio("填充方式演示", ["用均值填充 NaN", "用中位数填充 NaN"])
    if fill_choice == "用均值填充 NaN":
        filled = data_nan.copy()
        filled[np.isnan(filled)] = np.nanmean(data_nan)
    else:
        filled = data_nan.copy()
        filled[np.isnan(filled)] = np.nanmedian(data_nan)
    st.write("填充后数组：", np.round(filled, 2))


def page_normalize():
    """实验四：数据归一化（Min-Max）"""
    st.header("实验四：数据归一化（Min-Max）")
    st.markdown("公式：**x_norm = (x - min) / (max - min)**，将数据缩放到 [0, 1]。")

    use_preset = st.radio("数据来源", ["示例：高程序列 (m)", "自定义输入"], horizontal=True)
    if use_preset == "示例：高程序列 (m)":
        elevation = np.array([100, 250, 400, 550, 700, 850, 1000])
    else:
        text = st.text_input("输入一串数字，用逗号分隔", "100, 250, 400, 550, 700, 850, 1000")
        try:
            elevation = np.array([float(x.strip()) for x in text.split(",")])
        except Exception:
            elevation = np.array([100.0, 250.0, 400.0])
    if len(elevation) == 0:
        st.warning("请至少输入一个数")
        return
    elev_norm = (elevation - elevation.min()) / (elevation.max() - elevation.min() if elevation.max() != elevation.min() else 1)

    col1, col2 = st.columns(2)
    with col1:
        st.write("**原始数据**")
        st.write(pd.DataFrame({"高程(m)": elevation}))
    with col2:
        st.write("**归一化后 [0, 1]**")
        st.write(pd.DataFrame({"归一化值": np.round(elev_norm, 3)}))

    fig = make_subplots(rows=1, cols=2, subplot_titles=("原始高程", "归一化后"))
    fig.add_trace(go.Bar(x=list(range(len(elevation))), y=elevation, name="高程(m)"), row=1, col=1)
    fig.add_trace(go.Bar(x=list(range(len(elev_norm))), y=elev_norm, name="归一化"), row=1, col=2)
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)


def page_precipitation():
    """实验五：降水量统计"""
    st.header("实验五：降水量统计")
    st.markdown("模拟 12 个月降水量，计算年总量、月均、最湿/最干月。")

    seed = st.number_input("随机种子", 0, 99999, 42)
    np.random.seed(seed)
    monthly_rain = np.random.uniform(20, 150, 12)
    monthly_rain[5:8] *= 2  # 夏季偏多
    months = [f"{i+1}月" for i in range(12)]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("年总量 (mm)", f"{monthly_rain.sum():.1f}")
    with col2:
        st.metric("月均 (mm)", f"{monthly_rain.mean():.1f}")
    with col3:
        wet_idx = np.argmax(monthly_rain)
        dry_idx = np.argmin(monthly_rain)
        st.metric("最湿月 / 最干月", f"{months[wet_idx]} / {months[dry_idx]}")

    st.subheader("各月降水量")
    st.dataframe(pd.DataFrame({"月份": months, "降水量(mm)": np.round(monthly_rain, 1)}), use_container_width=True)

    fig = px.bar(x=months, y=monthly_rain, labels={"x": "月份", "y": "降水量 (mm)"}, title="月降水量")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def page_meshgrid():
    """实验六：经纬度网格（meshgrid）"""
    st.header("实验六：经纬度网格（meshgrid）")
    st.markdown("使用 `np.meshgrid` 生成规则经纬度网格，常用于格点数据、距离场等。")

    lon_min = st.number_input("经度范围最小值", 70.0, 140.0, 100.0)
    lon_max = st.number_input("经度范围最大值", 70.0, 140.0, 102.0)
    lat_min = st.number_input("纬度范围最小值", 15.0, 55.0, 30.0)
    lat_max = st.number_input("纬度范围最大值", 15.0, 55.0, 32.0)
    n_lon = st.slider("经度格点数", 2, 10, 3)
    n_lat = st.slider("纬度格点数", 2, 10, 3)

    lons = np.linspace(lon_min, lon_max, n_lon)
    lats = np.linspace(lat_min, lat_max, n_lat)
    Lon, Lat = np.meshgrid(lons, lats)

    st.subheader("经度网格")
    st.dataframe(pd.DataFrame(Lon).round(2), use_container_width=True)
    st.subheader("纬度网格")
    st.dataframe(pd.DataFrame(Lat).round(2), use_container_width=True)
    st.caption("每个 (i, j) 对应一个格点的 (经度, 纬度)")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=Lon.flatten(), y=Lat.flatten(), mode="markers+text",
        text=[f"({Lon.flat[i]:.1f},{Lat.flat[i]:.1f})" for i in range(Lon.size)],
        textposition="top center", marker=dict(size=12)
    ))
    fig.update_layout(
        title="格点分布",
        xaxis_title="经度 (°E)",
        yaxis_title="纬度 (°N)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
