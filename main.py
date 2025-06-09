from urllib.parse import urlencode
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Full Fat Search", page_icon=":mag:", layout="wide")
st.header("Full Fat Search Trend")


@st.cache_data
def get_data(q: str):
    sql = """
    select
    SUM(
        (LENGTH(lower(s.text)) - LENGTH(REPLACE(lower(s.text), lower(:search), ''))) / LENGTH(lower(:search))
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
    c = alt.Chart(df.reset_index()).mark_bar().encode(
        x=alt.X("fecha:T", title="fecha"),
        y=alt.Y("contador:Q", title="contador"),
        tooltip=[
            alt.Tooltip("contador:Q", title="Contador"),
            alt.Tooltip("video_title:N", title="Titulo"),
            alt.Tooltip("video_url:N", title="Video"),
        ],
    ).configure_mark(
        color="#ee2d6f"
    )
    st.altair_chart(c)
    st.dataframe(df, column_config={
        "video_url": st.column_config.LinkColumn("link"),
    })


default_search = st.query_params.get("buscar", "boludo")

q = st.text_input(
    "Buscar", placeholder="buscar...", value=default_search, label_visibility="hidden",
)

if q != default_search:
    st.query_params.update({"buscar": q})
    st.rerun()

buscar(q)