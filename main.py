import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Rail Transport Infrastructure",
    page_icon="🚆",
    layout="wide")

st.title("Rail Transport Infrastructure")
st.write("Інтерактивний аналіз інфраструктури рейкового транспорту у різних країнах світу.")

@st.cache_data
def load_data():
    df = pd.read_csv("data_RailTransport.csv")
    df["End Year numeric"] = pd.to_numeric(
        df["End Year"],
        errors="coerce")

    continent_map = {
        "Australia": "Океанія",
        "Canada": "Північна Америка",
        "US": "Північна Америка",
        "France": "Європа",
        "Germany": "Європа",
        "Italy": "Європа",
        "Norway": "Європа",
        "Spain": "Європа",
        "Sweden": "Європа",
        "UK": "Європа",
        "Denmark": "Європа",
        "Japan": "Азія",
        "Singapore": "Азія",
        "South Korea": "Азія"}

    df["Continent"] = df["Country"].map(continent_map)
    df["Environment"] = df["Environment"].replace(
        {"Paris-Nogent-sur-Seine": "Не визначено"})
    return df
df = load_data()


st.sidebar.header("Фільтри")

st.sidebar.write("Оберіть кількість станцій залізничного проєкту:")
station_filter = st.sidebar.selectbox("Кількість станцій", ["Усі значення", "1–10", "11–30", "31 і більше"])


st.sidebar.write("Оберіть частину світу, до якої належить проєкт:")
continent_filter = st.sidebar.selectbox("Частина світу", ["Усі частини світу", "Європа", "Азія", "Північна Америка", "Океанія"])

environment_filter = st.sidebar.selectbox("Середовище розташування",["Усі", "Urban", "Suburban", "Не визначено"])

status_filter = st.sidebar.selectbox("Статус проєкту", ["Усі"] + sorted(df["Status"].dropna().unique().tolist()))

project_filter = st.sidebar.selectbox("Тип проєкту",["Усі"] + sorted(df["Type of project"].dropna().unique().tolist()))

filtered_df = df.copy()

if station_filter == "1–10":
    filtered_df = filtered_df[
        filtered_df["Number of Stations"].between(1, 10)]

elif station_filter == "11–30":
    filtered_df = filtered_df[
        filtered_df["Number of Stations"].between(11, 30)]

elif station_filter == "31 і більше":
    filtered_df = filtered_df[
        filtered_df["Number of Stations"] >= 31]

if continent_filter != "Усі частини світу":
    filtered_df = filtered_df[
        filtered_df["Continent"] == continent_filter]

if environment_filter != "Усі":
    filtered_df = filtered_df[
        filtered_df["Environment"] == environment_filter]

if status_filter != "Усі":
    filtered_df = filtered_df[
        filtered_df["Status"] == status_filter]

if project_filter != "Усі":
    filtered_df = filtered_df[
        filtered_df["Type of project"] == project_filter]



tab1, tab2 = st.tabs(["Огляд та графіки", "Таблиця залізниць"])

with tab1:
    st.header("Загальна інформація")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Кількість проєктів", len(filtered_df))
    col2.metric( "Кількість країн", filtered_df["Country"].nunique())
    col3.metric("Загальна протяжність", f"{filtered_df['Length (Miles)'].sum():,.1f} миль")
    col4.metric("Кількість станцій", f"{filtered_df['Number of Stations'].sum():,}")
    st.divider()

    st.subheader("Перегляд повного датафрейму")
    st.write("Натисніть кнопку нижче, щоб переглянути весь датасет.")
    if st.button("Показати весь датафрейм"):
        st.session_state["show_dataframe"] = True
    if st.session_state.get("show_dataframe", False):
        valid_years = df["End Year numeric"].dropna()
        min_year = int(valid_years.min())
        max_year = int(valid_years.max())
        selected_years = st.slider("Оберіть діапазон років завершення будівництва:",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year))

        year_df = df[df["End Year numeric"].between(selected_years[0], selected_years[1])]

        st.dataframe(year_df.drop(columns=["End Year numeric"]), use_container_width=True)

        st.caption("Записи з невизначеним роком завершення не включаються до фільтрації за роками.")

    st.divider()
    st.header("Графічний аналіз")

    if filtered_df.empty:
        st.warning("За вибраними фільтрами даних не знайдено.")

    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Розподіл проєктів за середовищем")

            environment_data = (filtered_df["Environment"].value_counts().reset_index())

            environment_data.columns = ["Середовище", "Кількість проєктів"]
            environment_data["Середовище"] = (
                environment_data["Середовище"].replace({"Urban": "Міське", "Suburban": "Приміське"}))

            fig1 = px.pie(
                environment_data,
                names="Середовище",
                values="Кількість проєктів",
                hole=0.3)

            fig1.update_traces(textinfo="label+percent+value")

            st.plotly_chart(fig1,use_container_width=True)

            st.write("Діаграма демонструє співвідношення міських та приміських проєктів рейкового транспорту.")

        with col2:
            st.subheader("Кількість проєктів за роками")

            year_data = (
                filtered_df
                .dropna(subset=["End Year numeric"])
                .groupby("End Year numeric")
                .size()
                .reset_index(name="Кількість проєктів")
                .sort_values("End Year numeric"))

            year_data["Рік"] = (year_data["End Year numeric"].astype(int).astype(str))

            fig2 = px.bar(
                year_data,
                x="Рік",
                y="Кількість проєктів",
                labels={
                    "Рік": "Рік завершення",
                    "Кількість проєктів": "Кількість проєктів, од."})

            st.plotly_chart(fig2, use_container_width=True)

            st.write("Графік показує кількість проєктів, завершених у кожному році.")

        st.divider()
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Протяжність проєктів за країнами")

            country_data = (
                filtered_df
                .groupby("Country")["Length (Miles)"]
                .sum()
                .reset_index()
                .sort_values("Length (Miles)", ascending=False))

            fig3 = px.bar(
                country_data,
                x="Country",
                y="Length (Miles)",
                labels={"Country": "Країна", "Length (Miles)": "Протяжність, милі"})

            st.plotly_chart(fig3, use_container_width=True)
            st.write("Діаграма порівнює сумарну протяжність залізничних проєктів у різних країнах.")

        with col4:
            st.subheader("Вартість залежно від протяжності")

            fig4 = px.scatter(
                filtered_df.dropna(
                    subset=["Length (Miles)", "CPI adjusted (mil GBP)"]),
                x="Length (Miles)",
                y="CPI adjusted (mil GBP)",
                color="Country",
                hover_name="Project title",
                labels={"Length (Miles)": "Протяжність, милі", "CPI adjusted (mil GBP)": "Вартість, млн GBP", "Country": "Країна"})

            st.plotly_chart(fig4, use_container_width=True)
            st.write("Точкова діаграма показує залежність вартості проєкту від його протяжності. Вартість скоригована на інфляцію.")

    st.divider()

    st.header("Висновки")
    st.write("Дослідження датасету дає змогу проаналізувати розвиток рейкового транспорту в різних країнах світу. За допомогою фільтрів можна досліджувати проєкти "
        "за кількістю станцій, географічним розташуванням, статусом та типом будівництва.")
    st.write("Графічний аналіз дозволяє порівнювати кількість міських та приміських проєктів, досліджувати динаміку завершення будівництва, порівнювати протяжність залізничних ліній та їхню вартість.")

with tab2:

    st.header("Таблиця залізничних проєктів")
    st.write("Таблиця відображає проєкти, які відповідають вибраним фільтрам у бічній панелі.")

    table_df = filtered_df.copy()

    table_df["Країна та місто"] = (
        table_df["Country"].fillna("")
        + ", "
        + table_df["City"].fillna(""))

    display_df = table_df[["Project title", "Країна та місто", "Length (Miles)", "CPI adjusted (mil GBP)"]]

    display_df.columns = ["Назва залізниці", "Країна та місто", "Протяжність (милі)", "Вартість (млн GBP)"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.write(f"Кількість проєктів у таблиці: {len(display_df)}")

st.sidebar.divider()
st.sidebar.caption("Джерело даних: data_RailTransport.csv")
st.sidebar.caption("Rail Transport Infrastructure Dashboard")
