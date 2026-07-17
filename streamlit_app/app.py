"""Initial read-only Streamlit UI backed by application services."""

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from lotto_analysis.config import Settings
from lotto_analysis.database import create_database_engine
from lotto_analysis.repositories import PostgresDrawRepository
from streamlit_app.views.basic_statistics import render_basic_statistics
from streamlit_app.views.dashboard import render_dashboard
from streamlit_app.views.pattern_analysis import render_pattern_analysis


st.set_page_config(page_title="Lotto Analysis", page_icon="🎱", layout="wide")


@st.cache_resource
def _repository() -> PostgresDrawRepository:
    """Create and cache the PostgreSQL repository for the UI process."""
    settings = Settings.from_env()
    return PostgresDrawRepository(create_database_engine(settings))


def main() -> None:
    """Render the selected initial UI page."""
    st.title("한국 로또 6/45 분석")
    pages = {
        "대시보드": render_dashboard,
        "기본 통계": render_basic_statistics,
        "패턴 분석": render_pattern_analysis,
    }
    page = st.sidebar.radio("화면", tuple(pages))
    try:
        pages[page](_repository())
    except (SQLAlchemyError, ValueError, RuntimeError) as exc:
        st.error("화면을 불러오지 못했습니다: {0}".format(exc))


main()
