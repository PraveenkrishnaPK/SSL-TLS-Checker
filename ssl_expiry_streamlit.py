# ssl_expiry_streamlit.py
# Streamlit app to check SSL/TLS certificate expiration with enhanced UI and improved chart

import streamlit as st
import socket
import ssl
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import altair as alt

# --- Certificate inspection functions ---
def fetch_cert_expiry(host: str, port: int, timeout: float = 5.0) -> datetime:
    """Connect to host:port via SSL and return certificate expiry datetime."""
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert()
            return datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")


def check_host(host: str, port: int, warn_days: int) -> dict:
    """Return a dict of host check results."""
    try:
        expiry = fetch_cert_expiry(host, port)
        days_left = (expiry - datetime.utcnow()).days
        status = "OK" if days_left > warn_days else "WARNING"
        return {"host": host, "port": port, "expiry": expiry, "days_left": days_left, "status": status, "error": ""}
    except Exception as e:
        return {"host": host, "port": port, "expiry": None, "days_left": None, "status": "ERROR", "error": str(e)}


@st.cache_data
def run_checks(hosts: list[str], port: int, warn_days: int, workers: int) -> pd.DataFrame:
    """Run certificate checks in parallel and return a DataFrame."""
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(check_host, h, port, warn_days): h for h in hosts}
        total = len(futures)
        progress = st.progress(0)
        completed = 0
        for fut in as_completed(futures):
            results.append(fut.result())
            completed += 1
            progress.progress(completed / total)

    df = pd.DataFrame(results)
    df['expiry'] = pd.to_datetime(df['expiry'], errors='coerce')
    df['expiry_display'] = df['expiry'].dt.strftime('%Y-%m-%d %H:%M:%S').fillna('-')
    return df


# --- Streamlit UI setup ---
st.set_page_config(
    page_title="SSL/TLS Expiry Checker",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar form for inputs
with st.sidebar.form(key="settings_form"):
    st.header("⚙️ Settings")
    hosts_input = st.text_area("Enter hosts (one per line)", value="example.com")
    file_upload = st.file_uploader("…or upload a .txt file", type=["txt"])
    port = st.number_input("Port", value=443, min_value=1, max_value=65535)
    warn_days = st.number_input("Warn if expiring in ≤ days", value=15, min_value=0)
    workers = st.number_input("Concurrency (threads)", value=10, min_value=1)
    submitted = st.form_submit_button(label="🚀 Check Certificates")

# Main content
st.title("🔍 SSL/TLS Certificate Expiry Checker")
st.markdown("---")

if submitted:
    # Prepare host list
    if file_upload:
        content = file_upload.read().decode('utf-8')
        hosts = [h.strip() for h in content.splitlines() if h.strip()]
    else:
        hosts = [h.strip() for h in hosts_input.splitlines() if h.strip()]

    if not hosts:
        st.error("Please provide at least one hostname.")
    else:
        with st.spinner(f"Checking {len(hosts)} host(s)..."):
            df = run_checks(hosts, port, warn_days, workers)

        # Compute summary metrics
        total = len(df)
        ok = df[df['status'] == 'OK'].shape[0]
        warnings = df[df['status'] == 'WARNING'].shape[0]
        errors = df[df['status'] == 'ERROR'].shape[0]

        st.subheader("📊 Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Hosts", total)
        c2.metric("OK", ok, delta_color="inverse")
        c3.metric("Warnings", warnings)
        c4.metric("Errors", errors)

        # Improved chart: bucketed days left with custom colors and rotated labels
        st.subheader("📈 Certificate Expiry Buckets")
        df['days_left_bucket'] = pd.cut(
            df['days_left'].fillna(-1),
            bins=[-999, 0, 7, 30, 90, 365, 9999],
            labels=['Expired', '0-7 days', '8-30 days', '31-90 days', '91-365 days', '>365 days'],
            ordered=True
        )
        bucket_counts = df['days_left_bucket'].value_counts().sort_index().reset_index()
        bucket_counts.columns = ['Time Frame', 'Count']

        color_scale = alt.Scale(
            domain=['Expired', '0-7 days', '8-30 days', '31-90 days', '91-365 days', '>365 days'],
            range=['#ef5350', '#ffa726', '#fff176', '#aed581', '#64b5f6', '#90caf9']
        )

        chart = (
            alt.Chart(bucket_counts)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X('Time Frame', sort=list(bucket_counts['Time Frame']), axis=alt.Axis(labelAngle=-45, labelFontSize=12)),
                y=alt.Y('Count', title='Number of Hosts'),
                color=alt.Color('Time Frame', scale=color_scale, legend=None),
                tooltip=[alt.Tooltip('Time Frame'), alt.Tooltip('Count')]
            )
            .properties(width='container', height=350)
        )
        st.altair_chart(chart, use_container_width=True)

        # Detailed results table
        st.subheader("📝 Detailed Results")
        def highlight_row(row):
            if row.status == "WARNING":
                return ['background-color: #fff59d'] * len(row)
            if row.status == "ERROR":
                return ['background-color: #ef5350; color: white'] * len(row)
            return [''] * len(row)

        with st.expander("Show results table"):
            display_df = df[['host', 'port', 'expiry_display', 'days_left', 'status', 'error']]
            display_df = display_df.rename(columns={'expiry_display':'Expiry', 'days_left':'Days Left'})
            styled = display_df.style.apply(highlight_row, axis=1)
            st.dataframe(styled, height=400)

            # Downloads
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "ssl_expiry.csv", "text/csv")
            json_str = display_df.to_json(orient='records')
            st.download_button("📥 Download JSON", json_str, "ssl_expiry.json", "application/json")

        st.markdown("---")
        st.caption("Developed by Praveen A")
else:
    st.info("Configure settings in the sidebar and click **Check Certificates**.")
