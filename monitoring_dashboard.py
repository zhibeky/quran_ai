import os
import pandas as pd
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
from postgrest import APIError

st.set_page_config(page_title="Quran AI Monitoring", layout="wide")

st.title("Quran AI Monitoring Dashboard")
st.caption("User feedback collection + operational metrics")

# Load env from .env if present
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
if not supabase_url or not supabase_key:
    st.error("Supabase credentials are missing. Set SUPABASE_URL and SUPABASE_ANON_KEY.")
    st.stop()

sb = create_client(supabase_url, supabase_key)

@st.cache_data(ttl=30)
def load_data():
    def safe_fetch(table_name: str, order_col: str):
        try:
            data = sb.table(table_name).select("*").order(order_col).execute().data or []
            return pd.DataFrame(data)
        except APIError as e:
            if getattr(e, 'message', '') and "schema cache" in str(e.message):
                # Table likely missing; render empty until user runs SQL setup
                return pd.DataFrame()
            # Other API errors
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    msgs_df = safe_fetch("messages", "created_at")
    fdbk_df = safe_fetch("feedback", "created_at")
    users_df = safe_fetch("users", "created_at")
    return msgs_df, fdbk_df, users_df

messages_df, feedback_df, users_df = load_data()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Users", int(users_df.shape[0]) if not users_df.empty else 0)
with col2:
    st.metric("Total Messages", int(messages_df.shape[0]) if not messages_df.empty else 0)
with col3:
    st.metric("Avg Response Time (ms)", int(messages_df["response_time_ms"].mean()) if not messages_df.empty else 0)
with col4:
    st.metric("Avg Rating", round(feedback_df["rating"].mean(), 2) if not feedback_df.empty else 0)

st.divider()

tab1, tab2, tab3 = st.tabs(["Usage", "Performance", "Feedback"])

with tab1:
    st.subheader("Messages per Day")
    if not messages_df.empty:
        m = messages_df.copy()
        m["date"] = pd.to_datetime(m["created_at"]).dt.date
        st.bar_chart(m.groupby("date").size())
    else:
        st.info("No message data yet.")

    st.subheader("Active Users per Day")
    if not users_df.empty:
        u = users_df.copy()
        u["day"] = pd.to_datetime(u["last_seen"]).dt.date
        st.line_chart(u.groupby("day").size())
    else:
        st.info("No user data yet.")

with tab2:
    st.subheader("Response Time Distribution")
    if not messages_df.empty:
        st.area_chart(messages_df[["response_time_ms"]])
    else:
        st.info("No performance data yet.")

    st.subheader("Messages by Hour of Day")
    if not messages_df.empty:
        mh = messages_df.copy()
        mh["hour"] = pd.to_datetime(mh["created_at"]).dt.hour
        st.bar_chart(mh.groupby("hour").size())
    else:
        st.info("No temporal data yet.")

with tab3:
    st.subheader("Feedback Ratings Over Time")
    if not feedback_df.empty:
        f = feedback_df.copy()
        f["ts"] = pd.to_datetime(f["created_at"]) 
        st.line_chart(f.set_index("ts")["rating"])
    else:
        st.info("No feedback yet.")

    st.subheader("Rating Distribution")
    if not feedback_df.empty:
        st.bar_chart(feedback_df["rating"].value_counts().sort_index())
    else:
        st.info("No ratings to show.")

st.divider()
st.caption("Charts: messages/day, active users/day, response time distribution, messages by hour, ratings over time, rating distribution")


