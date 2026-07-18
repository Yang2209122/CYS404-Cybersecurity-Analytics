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

API_BASE_URL = (
    "https://cys404-cybersecurity-analytics.onrender.com"
)

PREDICT_URL = f"{API_BASE_URL}/predict"
HEALTH_URL = f"{API_BASE_URL}/health"

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "clustered_incidents.csv"


# Load the clustered dataset

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)

    data["Year"] = pd.to_numeric(
        data["Year"],
        errors="coerce"
    )

    return data


df = load_data()


# Header

st.title("Cybersecurity Incident Analytics")

st.write(
    "Explore cybersecurity incident trends and risk profiles, "
    "and predict the resolution time of a new incident."
)


# Sidebar filters

st.sidebar.header("Data Filters")

minimum_year = int(df["Year"].min())
maximum_year = int(df["Year"].max())

selected_years = st.sidebar.slider(
    "Year Range",
    min_value=minimum_year,
    max_value=maximum_year,
    value=(minimum_year, maximum_year)
)

country_options = [
    "All"
] + sorted(df["Country"].dropna().unique().tolist())

selected_country = st.sidebar.selectbox(
    "Country",
    country_options
)

attack_type_options = sorted(
    df["Attack Type"].dropna().unique().tolist()
)

selected_attack_types = st.sidebar.multiselect(
    "Attack Type",
    attack_type_options,
    default=attack_type_options
)


# Apply filters
filtered_df = df[
    df["Year"].between(
        selected_years[0],
        selected_years[1]
    )
].copy()

if selected_country != "All":
    filtered_df = filtered_df[
        filtered_df["Country"] == selected_country
    ]

if selected_attack_types:
    filtered_df = filtered_df[
        filtered_df["Attack Type"].isin(
            selected_attack_types
        )
    ]
else:
    filtered_df = filtered_df.iloc[0:0]


# Application tabs

overview_tab, trends_tab, prediction_tab = st.tabs(
    [
        "Overview",
        "Trends and Risk Profiles",
        "Resolution Time Prediction"
    ]
)


# Tab 1: Overview

with overview_tab:
    st.subheader("Incident Overview")

    if filtered_df.empty:
        st.warning(
            "No records match the selected filters."
        )

    else:
        metric_1, metric_2, metric_3, metric_4 = (
            st.columns(4)
        )

        metric_1.metric(
            "Total Incidents",
            f"{len(filtered_df):,}"
        )

        metric_2.metric(
            "Average Financial Loss",
            (
                f"${filtered_df[
                    'Financial Loss (in Million $)'
                ].mean():,.2f}M"
            )
        )

        metric_3.metric(
            "Average Affected Users",
            (
                f"{filtered_df[
                    'Number of Affected Users'
                ].mean():,.0f}"
            )
        )

        metric_4.metric(
            "Average Resolution Time",
            (
                f"{filtered_df[
                    'Incident Resolution Time (in Hours)'
                ].mean():.2f} hours"
            )
        )

        st.subheader("Filtered Incident Records")

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )


# Tab 2: Trends and risk profiles

with trends_tab:
    if filtered_df.empty:
        st.warning(
            "No records are available for visualisation."
        )

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

        loss_figure.update_layout(
            xaxis_title="Year",
            yaxis_title="Total Financial Loss (Million $)"
        )

        st.plotly_chart(
            loss_figure,
            use_container_width=True
        )


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
                y="Incident Count"
            )

            st.plotly_chart(
                attack_figure,
                use_container_width=True
            )


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

            st.plotly_chart(
                risk_figure,
                use_container_width=True
            )


        st.subheader("Risk-Profile Summary")

        risk_summary = (
            filtered_df
            .groupby("Risk Profile", as_index=False)
            .agg(
                Incident_Count=(
                    "Risk Profile",
                    "size"
                ),
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

        risk_summary[
            "Average_Financial_Loss"
        ] = risk_summary[
            "Average_Financial_Loss"
        ].round(2)

        risk_summary[
            "Average_Affected_Users"
        ] = risk_summary[
            "Average_Affected_Users"
        ].round(0)

        risk_summary[
            "Average_Resolution_Time"
        ] = risk_summary[
            "Average_Resolution_Time"
        ].round(2)

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
        "The application will send the input to the "
        "deployed FastAPI endpoint on Render."
    )

    try:
        health_response = requests.get(
            HEALTH_URL,
            timeout=15
        )

        if health_response.status_code == 200:
            st.success("Prediction API is online.")
        else:
            st.warning(
                "The API is responding but may not be healthy."
            )

    except requests.RequestException:
        st.warning(
            "The API status could not be checked. "
            "You may still attempt a prediction."
        )


    with st.form("prediction_form"):
        left_input, right_input = st.columns(2)

        with left_input:
            country = st.selectbox(
                "Country",
                sorted(
                    df["Country"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

            year = st.number_input(
                "Year",
                min_value=2015,
                max_value=2024,
                value=2024,
                step=1
            )

            attack_type = st.selectbox(
                "Attack Type",
                sorted(
                    df["Attack Type"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

            target_industry = st.selectbox(
                "Target Industry",
                sorted(
                    df["Target Industry"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

            financial_loss = st.number_input(
                "Financial Loss (Million $)",
                min_value=0.0,
                value=float(
                    df[
                        "Financial Loss (in Million $)"
                    ].median()
                ),
                step=1.0
            )


        with right_input:
            affected_users = st.number_input(
                "Number of Affected Users",
                min_value=0,
                value=int(
                    df[
                        "Number of Affected Users"
                    ].median()
                ),
                step=1000
            )

            attack_source = st.selectbox(
                "Attack Source",
                sorted(
                    df["Attack Source"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

            vulnerability = st.selectbox(
                "Security Vulnerability Type",
                sorted(
                    df[
                        "Security Vulnerability Type"
                    ]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

            defense_mechanism = st.selectbox(
                "Defense Mechanism Used",
                sorted(
                    df["Defense Mechanism Used"]
                    .dropna()
                    .unique()
                    .tolist()
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
            "financial_loss_million": float(
                financial_loss
            ),
            "affected_users": int(affected_users),
            "attack_source": attack_source,
            "security_vulnerability_type":
                vulnerability,
            "defense_mechanism_used":
                defense_mechanism
        }

        try:
            with st.spinner(
                "Requesting a prediction from the API..."
            ):
                prediction_response = requests.post(
                    PREDICT_URL,
                    json=request_data,
                    timeout=120
                )

            if prediction_response.status_code == 200:
                prediction_result = (
                    prediction_response.json()
                )

                predicted_hours = prediction_result[
                    "predicted_resolution_time_hours"
                ]

                st.success(
                    "Prediction completed successfully."
                )

                st.metric(
                    "Predicted Resolution Time",
                    f"{predicted_hours:.2f} hours"
                )

            else:
                st.error(
                    f"API error "
                    f"{prediction_response.status_code}: "
                    f"{prediction_response.text}"
                )

        except requests.exceptions.Timeout:
            st.error(
                "The request timed out. Please try again."
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "The application could not connect "
                "to the prediction API."
            )

        except Exception as error:
            st.error(
                f"Unexpected error: {error}"
            )