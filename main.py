from urllib.parse import urlencode, parse_qs
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Full Fat Search", page_icon=":mag:", layout="wide")
st.header("Full Fat Search Trend")


@st.cache_data
def get_data(q: str):
    sql = """
    select
    SUM(
        (LENGTH(s.text) - LENGTH(REPLACE(s.text, :search, ''))) / LENGTH(:search)
    ) AS contador,
    s.video_title,
    v.video_url,
    date(v.upload_date) as fecha
    from
    subtitles_with_videos s
    join videos v on s.video_id = v.video_id
    where
    subtitle_id in (
        select
        rowid
        from
        subtitles_fts
        where
        subtitles_fts match :search
    )
    group by
    s.video_title,
    v.video_url,
    v.upload_date
    """
    url = f"https://fullfatsearch.fly.dev/youtube.csv?{urlencode({'sql': sql, 'search': q, '_size': 'max'})}"
    df = pd.read_csv(url)
    df["fecha"] = pd.to_datetime(df.fecha)
    df = df.set_index("fecha")
    df = df.sort_values("contador", ascending=False)
    return df


def buscar(q: str):
    df = get_data(q)
    st.bar_chart(df, y="contador", color="#ee2d6f")
    info = pd.DataFrame({
        "Fecha": df.index.strftime("%Y-%m-%d"),
        "Contador": df["contador"],
        "Titulo": df["video_title"],
        "Video": df["video_url"],
    })
    config = {
        "Fecha": st.column_config.DateColumn(),
        "Contador": st.column_config.NumberColumn(),
        "Titulo": st.column_config.TextColumn(),
        "Video": st.column_config.LinkColumn("Video"),
    }
    info.set_index("Fecha", inplace=True)
    st.dataframe(info, column_config=config)


default_search = st.query_params.get("buscar", "boludo")

q = st.text_input(
    "Buscar", placeholder="buscar...", value=default_search, label_visibility="hidden",
)

if q != default_search:
    st.query_params.update({"buscar": q})
    st.rerun()

buscar(q)