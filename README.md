# 🌌 NASA Exoplanet Discovery Explorer

An interactive **Streamlit dashboard** for exploring confirmed exoplanets from **NASA’s Exoplanet Archive**.  
This project allows users to analyze discovery trends, planet characteristics, habitability, and stellar systems using real scientific data.

---

## 🚀 Features

- 🪐 Explore **10,000+ confirmed exoplanets**
- 🔍 Advanced filters:
  - Discovery method
  - Discovery year
  - Planet radius & temperature
  - Planet type
  - Habitability score
- 📊 Interactive visualizations with **Altair**
- 🗄️ Fast querying using **SQLite database**
- 📥 Export filtered data as CSV
- 🌍 Custom **Habitability Score (0–100)**

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** – Web application framework
- **Pandas** – Data analysis & manipulation
- **SQLite** – Database
- **Altair** – Interactive charts & visualizations

---

## 📂 Project Structure
NASA-Exoplanet-Discovery-Explorer/
│
├── app.py # Main Streamlit dashboard
├── database_setup.py # Creates and initializes SQLite database
├── data_fetcher.py # Fetches data from NASA Exoplanet Archive
├── data_extraction.py # Cleans and processes raw data
├── exoplanets.db # SQLite database
├── requirements.txt # Project dependencies
└── README.md # Project documentation

---

## ▶️ How to Run the Project Locally

### 1️⃣ Clone the repository
- ```bash
git clone https://github.com/Praneel2309/nasa-exoplanet-discovery-explorer.git
cd nasa-exoplanet-discovery-explorer
### 2️⃣ Install dependencies
pip install -r requirements.txt

### 3️⃣ Create the database (run once)
python database_setup.py

### 4️⃣ Run the Streamlit app
streamlit run app.py

### 5️⃣ Open in browser
http://localhost:8501

## 🌍 Data Source

All data is sourced from the NASA Exoplanet Archive,
maintained by Caltech/IPAC under contract with NASA.

🔗 https://exoplanetarchive.ipac.caltech.edu/

## 🧠 Habitability Score Logic

The habitability score (0–100) is calculated using:

- 🌍 Planet radius (Earth-like range)

- 🌡️ Equilibrium temperature

- 🛰️ Orbital period

Planets with a score above 50 are considered potentially habitable candidates.

## 📌 Future Enhancements

- Live API updates from NASA

- Online deployment (Streamlit Cloud)

- Machine learning–based habitability prediction

- More advanced analytics & clustering

## 👨‍💻 Author

### Praneel Sharma

This project was built as a scientific data exploration and visualization application using real NASA datasets.

⭐ If you find this project useful, consider starring the repository!

