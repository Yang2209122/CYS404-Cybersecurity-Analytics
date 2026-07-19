# CYS404 Final Project

## Cybersecurity Incident Analytics and Resolution Time Prediction

## 1. Quick Access

### Online Streamlit Application

https://cys404-cybersecurity-analytics.streamlit.app

### FastAPI Service

https://cys404-cybersecurity-analytics.onrender.com

### FastAPI Swagger Documentation

https://cys404-cybersecurity-analytics.onrender.com/docs

### FastAPI Health Check

https://cys404-cybersecurity-analytics.onrender.com/health

The Streamlit link opens the complete interactive application. The Swagger documentation can be used to test the FastAPI `/predict` endpoint directly.

---

## 2. Project Overview

This project analyses the Global Cybersecurity Threats 2015–2024 dataset.

Part I was completed using Apache Spark. It includes data preparation, feature engineering, K-Means clustering, risk-profile analysis, Random Forest regression, model evaluation, baseline comparison, and residual analysis.

The cybersecurity incidents were grouped into descriptive risk profiles based mainly on financial loss and the number of affected users. A Random Forest regression model was also developed to predict incident resolution time.

Part II converts the analysis into an interactive web application. FastAPI is used as the prediction backend and is deployed on Render. Streamlit is used as the frontend for data visualisation, filtering, risk-profile exploration, and resolution-time prediction.

---

## 3. Main Features

The Streamlit application allows users to:

* Filter incidents by year, country, attack type, and target industry
* View summary statistics for the selected incidents
* Examine financial loss trends over time
* Compare the distribution of attack types and target industries
* Explore the risk profiles generated through K-Means clustering
* View the relationship between financial loss and affected users
* Download the filtered incident data
* Enter the characteristics of a new incident
* Obtain a predicted incident resolution time in hours and days

---

## 4. Project Files

```text
CME2209122_Final_Project.ipynb
main.py
streamlit_app.py
model.joblib
clustered_incidents.csv
requirements.txt
.python-version
sample_request.json
README.md
```

### File Descriptions

#### `CME2209122_Final_Project.ipynb`

Contains the complete Part I Apache Spark workflow, including:

* Data loading and inspection
* Missing-value handling
* Data cleaning
* Feature engineering
* K-Means clustering
* Cluster evaluation
* Risk-profile interpretation
* Spark Random Forest regression
* RMSE, MAE, and R² evaluation
* Mean baseline comparison
* Residual analysis
* Deployment model export

#### `main.py`

Contains the FastAPI backend, including:

* Joblib model loading
* Input-data validation
* Root route
* Health-check route
* `/predict` endpoint
* Prediction response handling

#### `streamlit_app.py`

Contains the Streamlit frontend, including:

* Interactive filters
* Summary metrics
* Trend charts
* Risk-profile charts
* Risk-profile summary table
* Downloadable filtered data
* Prediction input form
* FastAPI integration

#### `model.joblib`

Contains the Random Forest deployment pipeline used by FastAPI.

#### `clustered_incidents.csv`

Contains the cleaned incident records together with the cluster number and descriptive risk profile generated in Part I.

#### `requirements.txt`

Lists the Python packages required to run the FastAPI and Streamlit applications.

#### `.python-version`

Specifies the Python version used for cloud deployment.

#### `sample_request.json`

Contains an example request for testing the FastAPI prediction endpoint.

---

## 5. Deployment Model

The deployment model was designed to remain consistent with the Spark model used in Part I.

It uses:

* The same cleaned dataset
* The same input features
* The same target variable
* The same Random Forest regression approach
* The same categorical and numerical information

For lightweight web deployment, the deployment version was implemented as a scikit-learn pipeline and exported as a Joblib file.

The Spark model and its evaluation remain the main model analysis in Part I. The Joblib version is used specifically by FastAPI to provide predictions in Part II.

---

## 6. Run the Streamlit Application Locally

### Step 1: Open the project folder

Open a terminal in the folder containing:

streamlit_app.py
clustered_incidents.csv
requirements.txt

### Step 2: Install the required packages

pip install -r requirements.txt

### Step 3: Start Streamlit

streamlit run streamlit_app.py

The application should open automatically in a browser.

The default local address is:

http://localhost:8501

The Streamlit application sends prediction requests to the deployed FastAPI service on Render.

---

## 7. Run the FastAPI Service Locally

### Step 1: Install the required packages

pip install -r requirements.txt

### Step 2: Start FastAPI

uvicorn main:app --reload

The local API will normally be available at:

http://127.0.0.1:8000

The local Swagger documentation will normally be available at:

http://127.0.0.1:8000/docs

The local health-check route will normally be available at:

http://127.0.0.1:8000/health

---

## 8. Example Prediction Request

```json
{
  "country": "China",
  "year": 2019,
  "attack_type": "Phishing",
  "target_industry": "Education",
  "financial_loss_million": 80.53,
  "affected_users": 773169,
  "attack_source": "Hacker Group",
  "security_vulnerability_type": "Unpatched Software",
  "defense_mechanism_used": "VPN"
}
```

## 9. Example Prediction Response

```json
{
  "predicted_resolution_time_hours": 36.42
}
```

The exact predicted value depends on the incident characteristics submitted to the model.

---

## 10. Testing the API through Swagger

1. Open:

   https://cys404-cybersecurity-analytics.onrender.com/docs

2. Select:

   POST /predict

3. Click:

   Try it out

4. Enter the example JSON request.

5. Click:

   Execute

6. Check the returned prediction under the response body.

---

## 11. Technologies Used

* Apache Spark
* Spark ML
* Python
* Pandas
* Scikit-learn
* Joblib
* FastAPI
* Uvicorn
* Streamlit
* Plotly
* Render
* Streamlit Community Cloud

---

## 12. Online Links Summary

| Service               | URL                                                        |
| --------------------- | ---------------------------------------------------------- |
| Streamlit Application | https://cys404-cybersecurity-analytics.streamlit.app       |
| FastAPI Service       | https://cys404-cybersecurity-analytics.onrender.com        |
| Swagger Documentation | https://cys404-cybersecurity-analytics.onrender.com/docs   |
| Health Check          | https://cys404-cybersecurity-analytics.onrender.com/health |
