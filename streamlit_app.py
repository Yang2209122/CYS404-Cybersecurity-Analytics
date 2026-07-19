from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# Application configuration
st.set_page_config(
    page_title="Cybersecurity Incident Analytics",
    layout="wide"
)

API_BASE_URL = "https://cys404-cybersecurity-analytics.onrender.com"
PREDICT_URL = f"{API_BASE_URL}/predict"
HEALTH_URL = f"{API_BASE_URL}/health"

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "clustered_incidents.csv"


@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)

    numeric_columns = [
        "Year",
        "Financial Loss (in Million $)",
        "Number of Affected Users",
        "Incident Resolution Time (in Hours)"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    return data


@st.cache_data(ttl=60, show_spinner=False)
def check_api_health():
    try:
        response = requests.get(HEALTH_URL, timeout=15)
        return response.status_code == 200
    except requests.RequestException:
        return False


df = load_data()

st.title("Cybersecurity Incident Analytics")
st.write(
    "Explore cybersecurity incident trends and risk profiles, "
    "and predict the resolution time of a new incident."
)
st.caption(
    f"Dataset coverage: {int(df['Year'].min())}-{int(df['Year'].max())} | "
    f"{len(df):,} incidents | {df['Risk Profile'].nunique()} risk profiles"
)


# Sidebar filters
st.sidebar.header("Data Filters")

minimum_year = int(df["Year"].min())
maximum_year = int(df["Year"].max())

selected_years = st.sidebar.slider(
    "Year Range",
    minimum_year,
    maximum_year,
    (minimum_year, maximum_year)
)

selected_country = st.sidebar.selectbox(
    "Country",
    ["All"] + sorted(df["Country"].dropna().unique().tolist())
)

attack_type_options = sorted(
    df["Attack Type"].dropna().unique().tolist()
)
selected_attack_types = st.sidebar.multiselect(
    "Attack Type",
    attack_type_options,
    default=attack_type_options
)

selected_industry = st.sidebar.selectbox(
    "Target Industry",
    ["All"] + sorted(
        df["Target Industry"].dropna().unique().tolist()
    )
)


# Apply filters
filtered_df = df[
    df["Year"].between(selected_years[0], selected_years[1])
].copy()

if selected_country != "All":
    filtered_df = filtered_df[
        filtered_df["Country"] == selected_country
    ]

if selected_attack_types:
    filtered_df = filtered_df[
        filtered_df["Attack Type"].isin(selected_attack_types)
    ]
else:
    filtered_df = filtered_df.iloc[0:0]

if selected_industry != "All":
    filtered_df = filtered_df[
        filtered_df["Target Industry"] == selected_industry
    ]

st.sidebar.divider()
st.sidebar.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} incidents"
)

if check_api_health():
    st.sidebar.success("Prediction API: Online")
else:
    st.sidebar.warning("Prediction API: Unavailable")


# Application tabs
overview_tab, trends_tab, prediction_tab = st.tabs([
    "Overview",
    "Trends and Risk Profiles",
    "Resolution Time Prediction"
])


# Tab 1: Overview
with overview_tab:
    st.subheader("Incident Overview")

    if filtered_df.empty:
        st.warning("No records match the selected filters.")

    else:
        metric_1, metric_2, metric_3, metric_4 = st.columns(4)

        metric_1.metric("Total Incidents", f"{len(filtered_df):,}")
        metric_2.metric(
            "Average Financial Loss",
            f"${filtered_df['Financial Loss (in Million $)'].mean():,.2f}M"
        )
        metric_3.metric(
            "Average Affected Users",
            f"{filtered_df['Number of Affected Users'].mean():,.0f}"
        )
        metric_4.metric(
            "Average Resolution Time",
            f"{filtered_df['Incident Resolution Time (in Hours)'].mean():.2f} hours"
        )

        st.subheader("Key Insights")

        annual_loss = filtered_df.groupby("Year")[
            "Financial Loss (in Million $)"
        ].sum()

        highest_loss_year = int(annual_loss.idxmax())
        highest_loss_value = float(annual_loss.max())
        most_common_attack = filtered_df["Attack Type"].value_counts().idxmax()
        most_targeted_industry = (
            filtered_df["Target Industry"].value_counts().idxmax()
        )
        dominant_profile = filtered_df["Risk Profile"].value_counts().idxmax()

        insight_1, insight_2, insight_3 = st.columns(3)

        with insight_1:
            st.info(
                "**Highest-loss year**\n\n"
                f"{highest_loss_year}, with "
                f"${highest_loss_value:,.2f}M in total loss."
            )

        with insight_2:
            st.info(
                "**Most common attack and target**\n\n"
                f"{most_common_attack} was most frequent, while "
                f"{most_targeted_industry} was the most targeted industry."
            )

        with insight_3:
            st.info(
                "**Dominant risk profile**\n\n"
                f"{dominant_profile}."
            )

        st.download_button(
            "Download Filtered Data",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="filtered_cybersecurity_incidents.csv",
            mime="text/csv"
        )

        with st.expander(
            f"View Filtered Incident Records ({len(filtered_df):,})"
        ):
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )


# Tab 2: Trends and risk profiles
with trends_tab:
    if filtered_df.empty:
        st.warning("No records are available for visualisation.")

    else:
        st.subheader("Financial Loss over Time")

        loss_by_year = (
            filtered_df
            .groupby("Year", as_index=False)[
                "Financial Loss (in Million $)"
            ]
            .sum()
            .sort_values("Year")
        )

        loss_figure = px.line(
            loss_by_year,
            x="Year",
            y="Financial Loss (in Million $)",
            markers=True,
            labels={
                "Financial Loss (in Million $)":
                    "Total Financial Loss (Million $)"
            }
        )
        loss_figure.update_traces(
            hovertemplate=(
                "Year: %{x}<br>Total Loss: $%{y:,.2f}M"
                "<extra></extra>"
            )
        )
        st.plotly_chart(loss_figure, use_container_width=True)

        left_chart, right_chart = st.columns(2)

        with left_chart:
            st.subheader("Attack-Type Distribution")

            attack_distribution = (
                filtered_df["Attack Type"]
                .value_counts()
                .rename_axis("Attack Type")
                .reset_index(name="Incident Count")
            )

            attack_figure = px.bar(
                attack_distribution,
                x="Attack Type",
                y="Incident Count",
                text_auto=True
            )
            st.plotly_chart(attack_figure, use_container_width=True)

        with right_chart:
            st.subheader("Risk-Profile Breakdown")

            risk_distribution = (
                filtered_df["Risk Profile"]
                .value_counts()
                .rename_axis("Risk Profile")
                .reset_index(name="Incident Count")
            )

            risk_figure = px.pie(
                risk_distribution,
                names="Risk Profile",
                values="Incident Count",
                hole=0.35
            )
            risk_figure.update_traces(
                textposition="inside",
                textinfo="percent+label"
            )
            st.plotly_chart(risk_figure, use_container_width=True)

        resolution_chart, industry_chart = st.columns(2)

        with resolution_chart:
            st.subheader("Average Resolution Time by Attack Type")

            resolution_by_attack = (
                filtered_df
                .groupby("Attack Type", as_index=False)[
                    "Incident Resolution Time (in Hours)"
                ]
                .mean()
                .sort_values(
                    "Incident Resolution Time (in Hours)",
                    ascending=False
                )
            )
            resolution_by_attack[
                "Incident Resolution Time (in Hours)"
            ] = resolution_by_attack[
                "Incident Resolution Time (in Hours)"
            ].round(2)

            resolution_figure = px.bar(
                resolution_by_attack,
                x="Attack Type",
                y="Incident Resolution Time (in Hours)",
                text_auto=".2f",
                labels={
                    "Incident Resolution Time (in Hours)":
                        "Average Resolution Time (Hours)"
                }
            )
            st.plotly_chart(
                resolution_figure,
                use_container_width=True
            )

        with industry_chart:
            st.subheader("Incidents by Target Industry")

            industry_distribution = (
                filtered_df["Target Industry"]
                .value_counts()
                .rename_axis("Target Industry")
                .reset_index(name="Incident Count")
            )

            industry_figure = px.bar(
                industry_distribution,
                x="Target Industry",
                y="Incident Count",
                text_auto=True
            )
            st.plotly_chart(
                industry_figure,
                use_container_width=True
            )

        st.subheader("Risk-Profile Structure")
        st.caption(
            "The scatter plot uses the two features selected for "
            "K-Means clustering in Part I."
        )

        risk_scatter = px.scatter(
            filtered_df,
            x="Financial Loss (in Million $)",
            y="Number of Affected Users",
            color="Risk Profile",
            hover_data=[
                "Country",
                "Year",
                "Attack Type",
                "Target Industry",
                "Incident Resolution Time (in Hours)"
            ],
            opacity=0.60,
            render_mode="webgl"
        )
        st.plotly_chart(risk_scatter, use_container_width=True)

        st.subheader("Risk-Profile Summary")

        risk_summary = (
            filtered_df
            .groupby("Risk Profile", as_index=False)
            .agg(
                Incident_Count=("Risk Profile", "size"),
                Average_Financial_Loss=(
                    "Financial Loss (in Million $)",
                    "mean"
                ),
                Average_Affected_Users=(
                    "Number of Affected Users",
                    "mean"
                ),
                Average_Resolution_Time=(
                    "Incident Resolution Time (in Hours)",
                    "mean"
                )
            )
        )

        risk_summary.columns = [
            "Risk Profile",
            "Incident Count",
            "Average Financial Loss ($M)",
            "Average Affected Users",
            "Average Resolution Time (Hours)"
        ]
        risk_summary["Average Financial Loss ($M)"] = (
            risk_summary["Average Financial Loss ($M)"].round(2)
        )
        risk_summary["Average Affected Users"] = (
            risk_summary["Average Affected Users"].round(0).astype(int)
        )
        risk_summary["Average Resolution Time (Hours)"] = (
            risk_summary[
                "Average Resolution Time (Hours)"
            ].round(2)
        )

        st.dataframe(
            risk_summary,
            use_container_width=True,
            hide_index=True
        )


# Tab 3: Prediction interface
with prediction_tab:
    st.subheader("Predict Incident Resolution Time")
    st.write(
        "Enter the characteristics of a new incident. "
        "The application sends the input to the deployed "
        "FastAPI endpoint on Render."
    )

    if check_api_health():
        st.success("Prediction API is online.")
    else:
        st.warning(
            "The API status could not be confirmed. "
            "You may still attempt a prediction."
        )

    st.link_button(
        "Open FastAPI Documentation",
        f"{API_BASE_URL}/docs"
    )

    with st.form("prediction_form"):
        left_input, right_input = st.columns(2)

        with left_input:
            country = st.selectbox(
                "Country",
                sorted(df["Country"].dropna().unique().tolist())
            )
            year = st.number_input(
                "Year",
                min_value=minimum_year,
                max_value=maximum_year,
                value=maximum_year,
                step=1
            )
            attack_type = st.selectbox(
                "Attack Type",
                sorted(df["Attack Type"].dropna().unique().tolist())
            )
            target_industry = st.selectbox(
                "Target Industry",
                sorted(
                    df["Target Industry"].dropna().unique().tolist()
                )
            )
            financial_loss = st.number_input(
                "Financial Loss (Million $)",
                min_value=0.0,
                value=float(
                    df["Financial Loss (in Million $)"].median()
                ),
                step=1.0
            )

        with right_input:
            affected_users = st.number_input(
                "Number of Affected Users",
                min_value=0,
                value=int(
                    df["Number of Affected Users"].median()
                ),
                step=1000
            )
            attack_source = st.selectbox(
                "Attack Source",
                sorted(
                    df["Attack Source"].dropna().unique().tolist()
                )
            )
            vulnerability = st.selectbox(
                "Security Vulnerability Type",
                sorted(
                    df[
                        "Security Vulnerability Type"
                    ].dropna().unique().tolist()
                )
            )
            defense_mechanism = st.selectbox(
                "Defense Mechanism Used",
                sorted(
                    df[
                        "Defense Mechanism Used"
                    ].dropna().unique().tolist()
                )
            )

        submitted = st.form_submit_button(
            "Predict Resolution Time"
        )

    if submitted:
        request_data = {
            "country": country,
            "year": int(year),
            "attack_type": attack_type,
            "target_industry": target_industry,
            "financial_loss_million": float(financial_loss),
            "affected_users": int(affected_users),
            "attack_source": attack_source,
            "security_vulnerability_type": vulnerability,
            "defense_mechanism_used": defense_mechanism
        }

        try:
            with st.spinner(
                "Requesting a prediction from the API..."
            ):
                response = requests.post(
                    PREDICT_URL,
                    json=request_data,
                    timeout=120
                )

            if response.status_code == 200:
                result = response.json()
                predicted_hours = float(
                    result["predicted_resolution_time_hours"]
                )
                predicted_days = predicted_hours / 24
                historical_median = float(
                    df[
                        "Incident Resolution Time (in Hours)"
                    ].median()
                )
                difference = predicted_hours - historical_median

                lower_quartile = float(
                    df[
                        "Incident Resolution Time (in Hours)"
                    ].quantile(0.25)
                )
                upper_quartile = float(
                    df[
                        "Incident Resolution Time (in Hours)"
                    ].quantile(0.75)
                )

                if predicted_hours < lower_quartile:
                    interpretation = (
                        "Short relative to historical incidents"
                    )
                elif predicted_hours > upper_quartile:
                    interpretation = (
                        "Long relative to historical incidents"
                    )
                else:
                    interpretation = (
                        "Within the typical historical range"
                    )

                st.success("Prediction completed successfully.")

                result_1, result_2, result_3 = st.columns(3)
                result_1.metric(
                    "Predicted Resolution Time",
                    f"{predicted_hours:.2f} hours"
                )
                result_2.metric(
                    "Equivalent Duration",
                    f"{predicted_days:.2f} days"
                )
                result_3.metric(
                    "Difference from Historical Median",
                    f"{difference:+.2f} hours"
                )

                st.info(
                    f"**Historical interpretation:** {interpretation}."
                )

                with st.expander("View Submitted Incident Data"):
                    st.json(request_data)

            else:
                st.error(
                    f"API error {response.status_code}: "
                    f"{response.text}"
                )

        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")

        except requests.exceptions.ConnectionError:
            st.error(
                "The application could not connect "
                "to the prediction API."
            )

        except Exception as error:
            st.error(f"Unexpected error: {error}")
