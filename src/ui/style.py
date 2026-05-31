from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """Apply shared visual styling for the Streamlit portals."""
    st.markdown(
        """
        <style>
            :root {
                --hotel-primary: #7c2d12;
                --hotel-primary-dark: #431407;
                --hotel-accent: #f59e0b;
                --hotel-surface: #ffffff;
                --hotel-muted: #6b7280;
                --hotel-border: #e5e7eb;
                --hotel-bg: #f8fafc;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(245, 158, 11, 0.12), transparent 28rem),
                    linear-gradient(180deg, #fffaf0 0%, var(--hotel-bg) 18rem);
            }

            .block-container {
                padding-top: 1.6rem;
                max-width: 1180px;
            }

            [data-testid="stSidebar"] {
                background: #ffffff;
                border-right: 1px solid var(--hotel-border);
            }

            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3 {
                color: var(--hotel-primary-dark);
            }

            h1, h2, h3 {
                color: #111827;
                letter-spacing: -0.02em;
            }

            .hotel-hero {
                background: linear-gradient(135deg, #431407 0%, #7c2d12 58%, #b45309 100%);
                border-radius: 24px;
                padding: 1.5rem 1.7rem;
                color: #fff7ed;
                box-shadow: 0 18px 45px rgba(67, 20, 7, 0.18);
                margin-bottom: 1rem;
            }

            .hotel-hero-label {
                color: #fed7aa;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.13em;
                text-transform: uppercase;
                margin-bottom: 0.35rem;
            }

            .hotel-hero h1 {
                color: #fff7ed;
                margin: 0;
                font-size: 2.1rem;
            }

            .hotel-hero p {
                margin: 0.55rem 0 0;
                max-width: 760px;
                color: #ffedd5;
                font-size: 1rem;
            }

            .hotel-page-title {
                background: var(--hotel-surface);
                border: 1px solid var(--hotel-border);
                border-radius: 18px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
                box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
            }

            .hotel-page-title h2 {
                margin: 0;
                font-size: 1.45rem;
            }

            .hotel-page-title p {
                color: var(--hotel-muted);
                margin: 0.35rem 0 0;
            }

            .hotel-status-card {
                background: #fff;
                border: 1px solid var(--hotel-border);
                border-radius: 16px;
                padding: 0.85rem 1rem;
                margin-bottom: 0.85rem;
                box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
            }

            .hotel-muted {
                color: var(--hotel-muted);
            }

            div.stButton > button,
            div.stFormSubmitButton > button {
                border-radius: 999px;
                border: 1px solid rgba(124, 45, 18, 0.25);
                font-weight: 650;
            }

            div.stButton > button[kind="primary"],
            div.stFormSubmitButton > button[kind="primary"] {
                background: var(--hotel-primary);
            }

            [data-testid="stMetric"] {
                background: #ffffff;
                border: 1px solid var(--hotel-border);
                border-radius: 16px;
                padding: 1rem;
                box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
            }

            div[data-testid="stDataFrame"],
            div[data-testid="stTable"] {
                border-radius: 14px;
                overflow: hidden;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.5rem;
            }

            .stTabs [data-baseweb="tab"] {
                border-radius: 999px;
                padding: 0.45rem 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, description: str = "") -> None:
    description_html = f"<p>{description}</p>" if description else ""
    st.markdown(
        f"""
        <div class="hotel-page-title">
            <h2>{title}</h2>
            {description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, label: str = "Hotel Reservation System") -> None:
    st.markdown(
        f"""
        <div class="hotel-hero">
            <div class="hotel-hero-label">{label}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
