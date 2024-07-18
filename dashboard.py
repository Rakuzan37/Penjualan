import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objs as go
import plotly.express as px

st.title("Dashboard Penjualan")

data = pd.read_csv("https://docs.google.com/spreadsheets/d/17pJFUizbgtInkDCRS1TNvFLXxv9s3QwofdvQGghE97I/export?format=csv")
data["Tanggal"] = pd.to_datetime(data["Tanggal"])

data_growth = data.set_index("Tanggal").pct_change().reset_index()
data_growth.iloc[:, 1:] = data_growth.iloc[:, 1:] * 100

start_date = pd.to_datetime(st.date_input(label = "Tanggal   Mulai", min_value = datetime.date(1900, 1, 1)))
end_date = pd.to_datetime(st.date_input(label = "Tanggal Selesai", min_value = datetime.date(1900, 1, 1)))

data_filtered = data[(data["Tanggal"] >= start_date) & (data["Tanggal"] <= end_date)].copy()

for col in data_filtered.columns[1:]:
    data_filtered[f"{col}_pct_change"] = data_filtered[col].pct_change() * 100

st.subheader("Grafik Penjualan")
selected_stands = st.multiselect("Pilih Lapak", data.columns[1:], default = ["Total"])

fig = go.Figure()

for stand in selected_stands:
    fig.add_trace(go.Scatter(
        x = data_filtered["Tanggal"],
        y = data_filtered[stand],
        mode = "lines+markers",
        name = stand,
        hoverinfo = "x+y+name+text",
        text = [f"% Change: {pct_change:.2f}%" for pct_change in data_filtered[f"{stand}_pct_change"]]
    ))

fig.update_layout(
    title = "Grafik Penjualan per Lapak",
    xaxis_title = "Tanggal",
    yaxis_title = "Penjualan",
    yaxis_tickformat = ',',
    legend_title = "Lapak",
    template = "plotly_white",
    hovermode = "x"
)

fig.update_xaxes(tickangle = 45)

st.plotly_chart(fig, use_container_width = True)



st.subheader("Grafik Perbandingan Setiap Lapak")

date = pd.to_datetime(st.date_input(label = "Tanggal", min_value = datetime.date(1900, 1, 1)))

data_filtered = data[(data["Tanggal"] == date)].copy()
growth_filtered = data_growth[data_growth["Tanggal"] == date].copy()

data_melt = data_filtered.iloc[:,1:-2].melt(var_name = "Lapak", value_name = "Penjualan")
growth_melt = growth_filtered.iloc[:,1:-2].melt(var_name = "Lapak", value_name = "Pertumbuhan")

fig_pie = px.pie(data_melt, names = "Lapak", values = "Penjualan", title = "Perbandingan setiap lapak")
st.plotly_chart(fig_pie)

top_3_lapak = data_melt.nlargest(3, "Penjualan")
top_3_growth = growth_melt.nlargest(3, "Pertumbuhan")

fig_bar = px.bar(top_3_lapak, x = "Lapak", y = "Penjualan", title = "Top 3 Penghasilan Lapak", labels = {"Penjualan": "Penghasilan"})
st.plotly_chart(fig_bar)

fig_bar = px.bar(top_3_growth, x="Lapak", y="Pertumbuhan", title="Top 3 Pertumbuhan Penghasilan Lapak", labels={"Pertumbuhan": "Pertumbuhan (%)"})
st.plotly_chart(fig_bar)
