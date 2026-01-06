# Louisville, KY Property Foreclosures Dashboard

This project provides an interactive web dashboard for visualizing property foreclosure data in Louisville, Kentucky. It includes a Go script to fetch and format the data from the Louisville Metro ArcGIS API and a Python-based Streamlit application to display the data with interactive filters and charts.

<img src="images/Screenshot.png" alt="Image of App" width="400"/>


## Features

- **Automated Data Fetching:** A Go script downloads the latest foreclosure data and formats it into a clean CSV file.
- **Interactive Dashboard:** A Dashboard with Streamlit allows for easy data exploration.
- **Dynamic Filtering:** Filter foreclosures by Neighborhood and Year.
- **Key Metrics:** View at-a-glance statistics like total foreclosures, top zip code, and peak months for filings and sales.
- **Visualizations:** An interactive bar chart shows the distribution of foreclosures across different neighborhoods.
- **Detailed Data Table:** Browse and search through the cleaned and formatted foreclosure records.

## Project Structure

The project is organized into three main files:

- fetchData.go: A Go program responsible for fetching data in batches from the ArcGIS REST API. It handles data formatting, including date conversion and cleaning null values, and saves the final output as a CSV file.

- helper.py: A Python module that contains all the logic for data processing and visualization. This includes functions for loading the CSV, converting data types, building addresses, calculating metrics, and creating plots.

- dashboard.py: The main Python script that runs the Streamlit web application. It defines the user interface, handles user input from the sidebar filters, and calls functions from helper.py to display the data and visualizations.

## Setup and Installation

Follow these steps to set up and run the project locally.

Prerequisites
- Go (version 1.18 or newer)

- Python (version 3.8 to 3.11)

Installation Steps

Clone the Repository

Set up Python Environment
Create and activate a virtual environment to manage project dependencies.

# Create the virtual environment
### Virtual Environment Commands
| Command | Linux/Mac | GitBash |
| ------- | --------- | ------- |
| Create | `python3 -m venv venv` | `python -m venv venv` |
| Activate | `source venv/bin/activate` | `source venv/Scripts/activate` |
| Install | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Deactivate | `deactivate` | `deactivate` |

## How to Run the Project

**The project is a two-step process:** first, you fetch the data with the Go script, and then you run the dashboard with Streamlit.

**Step 1:** Fetch the Data
Run the Go program from your terminal to download the foreclosure data. This will create a data/ directory and save the Louisville_Metro_KY_-_Property_Foreclosures.csv file inside it.

```bash
go run fetchData.go
```

You should see output indicating the fetch progress and a final confirmation message.

**Step 2:** Run the Streamlit Dashboard
Once the data has been downloaded, start the Streamlit application.

```bash
streamlit run src/dashboard.py
```

This command will start the web server and open the dashboard in your default web browser. You can now interact with the filters and visualizations.

## Data Source
The data is sourced from the official Louisville Metro Government Open Data portal, provided via an ArcGIS FeatureServer.

<!-- note to self run with /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m streamlit run src/dashboard.py
 python 3.14 not supported -->
