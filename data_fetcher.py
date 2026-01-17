"""
Enhanced Data Fetcher for NASA Exoplanet Archive
Fetches comprehensive exoplanet data with proper error handling
"""

import requests
import pandas as pd
import time
from datetime import datetime

def fetch_exoplanet_data():
    """
    Fetch ALL available exoplanet data from NASA API
    The API doesn't support pagination the way we thought - we need to fetch all at once
    
    Returns:
        pandas DataFrame with exoplanet data
    """
    
    base_url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    
    print(f"🚀 Fetching ALL exoplanet data from NASA...")
    print("=" * 60)
    
    # Comprehensive query with all useful fields - fetch everything at once
    query = """
    SELECT 
        pl_name, hostname, discoverymethod, disc_year, disc_facility,
        pl_orbper, pl_orbsmax, pl_rade, pl_radj, pl_masse, pl_massj,
        pl_bmasse, pl_bmassj, pl_bmassprov, pl_eqt, pl_insol, pl_dens,
        st_teff, st_rad, st_mass, st_met, st_logg, st_age,
        sy_snum, sy_pnum, sy_dist, sy_gaiamag,
        ra, dec, glat, glon
    FROM ps
    """
    
    params = {
        'query': query,
        'format': 'json'
    }
    
    try:
        print(f"📡 Connecting to NASA Exoplanet Archive...")
        
        response = requests.get(base_url, params=params, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✅ Success! Retrieved {len(data)} records")
        print("=" * 60)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        return df
        
    except requests.exceptions.Timeout:
        print(f"⚠️ Timeout occurred. The API might be slow. Please try again.")
        return pd.DataFrame()
        
    except Exception as e:
        print(f"✗ Error fetching data: {e}")
        return pd.DataFrame()


def clean_exoplanet_data(df):
    """
    Clean and enhance the fetched data
    """
    
    if df.empty:
        print("❌ No data to clean!")
        return df
    
    print("\n🧹 Cleaning data...")
    
    # Convert numeric columns
    numeric_columns = [
        'pl_orbper', 'pl_orbsmax', 'pl_rade', 'pl_radj', 'pl_masse', 'pl_massj',
        'pl_bmasse', 'pl_bmassj', 'pl_eqt', 'pl_insol', 'pl_dens',
        'st_teff', 'st_rad', 'st_mass', 'st_met', 'st_logg', 'st_age',
        'sy_snum', 'sy_pnum', 'sy_dist', 'sy_gaiamag',
        'ra', 'dec', 'glat', 'glon', 'disc_year'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove completely empty rows
    df = df.dropna(how='all')
    
    # Remove rows without planet name
    df = df.dropna(subset=['pl_name'])
    
    # Remove duplicates based on planet name
    initial_count = len(df)
    df = df.drop_duplicates(subset=['pl_name'], keep='first')
    duplicates_removed = initial_count - len(df)
    
    if duplicates_removed > 0:
        print(f"   ℹ️ Removed {duplicates_removed} duplicate planets")
    
    # Add calculated fields
    print("   🔬 Calculating derived metrics...")
    
    # 1. Habitability Score (0-100)
    df['habitability_score'] = calculate_habitability_score(df)
    
    # 2. Planet Type Classification
    df['planet_type'] = classify_planet_type(df)
    
    # 3. Discovery Era
    df['discovery_era'] = pd.cut(df['disc_year'], 
                                   bins=[0, 2000, 2010, 2015, 2020, 2030],
                                   labels=['Pre-2000', '2000s', '2010-2015', '2015-2020', '2020+'])
    
    # 4. Distance Category
    df['distance_category'] = pd.cut(df['sy_dist'],
                                       bins=[0, 50, 100, 500, 10000],
                                       labels=['Very Close (<50pc)', 'Close (50-100pc)', 
                                              'Moderate (100-500pc)', 'Far (>500pc)'])
    
    # Add metadata
    df['data_fetched_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"✅ Cleaning complete! Final dataset: {len(df)} planets")
    
    return df


def calculate_habitability_score(df):
    """
    Calculate a simple habitability score (0-100)
    Based on: radius, temperature, and orbital period
    """
    score = pd.Series(0, index=df.index)
    
    # Criterion 1: Earth-like radius (0.5 to 2 Earth radii) - 35 points
    if 'pl_rade' in df.columns:
        mask = (df['pl_rade'] >= 0.5) & (df['pl_rade'] <= 2.0)
        score = score + (mask.astype(int) * 35)
    
    # Criterion 2: Temperate zone (200K to 350K) - 40 points
    if 'pl_eqt' in df.columns:
        mask = (df['pl_eqt'] >= 200) & (df['pl_eqt'] <= 350)
        score = score + (mask.astype(int) * 40)
    
    # Criterion 3: Reasonable orbital period (200 to 500 days) - 25 points
    if 'pl_orbper' in df.columns:
        mask = (df['pl_orbper'] >= 200) & (df['pl_orbper'] <= 500)
        score = score + (mask.astype(int) * 25)
    
    return score


def classify_planet_type(df):
    """
    Classify planets by type based on radius
    """
    planet_type = pd.Series('Unknown', index=df.index)
    
    if 'pl_rade' in df.columns:
        # Create masks for each category
        planet_type = planet_type.where(~((df['pl_rade'] < 1.25) & df['pl_rade'].notna()), 'Rocky (Earth-like)')
        planet_type = planet_type.where(~((df['pl_rade'] >= 1.25) & (df['pl_rade'] < 2.0)), 'Super-Earth')
        planet_type = planet_type.where(~((df['pl_rade'] >= 2.0) & (df['pl_rade'] < 4.0)), 'Mini-Neptune')
        planet_type = planet_type.where(~((df['pl_rade'] >= 4.0) & (df['pl_rade'] < 10.0)), 'Neptune-like')
        planet_type = planet_type.where(~(df['pl_rade'] >= 10.0), 'Jupiter-like')
    
    return planet_type


def save_to_csv(df, filename='exoplanet_data.csv'):
    """
    Save DataFrame to CSV
    """
    if df.empty:
        print("❌ No data to save!")
        return
    
    df.to_csv(filename, index=False)
    print(f"\n💾 Data saved to {filename}")
    print(f"   Size: {len(df)} rows × {len(df.columns)} columns")


def main():
    """
    Main execution function
    """
    print("🌌 NASA Exoplanet Data Fetcher")
    print("=" * 60)
    
    # Fetch data
    raw_df = fetch_exoplanet_data()
    
    if raw_df.empty:
        print("\n❌ Failed to fetch data. Please check your internet connection and try again.")
        return
    
    # Clean data
    clean_df = clean_exoplanet_data(raw_df)
    
    if clean_df.empty:
        print("\n❌ Failed to clean data.")
        return
    
    # Save to CSV
    save_to_csv(clean_df)
    
    # Print summary
    print("\n📊 Dataset Summary:")
    print("=" * 60)
    print(f"Total Planets: {len(clean_df)}")
    
    if 'discoverymethod' in clean_df.columns:
        print(f"Discovery Methods: {clean_df['discoverymethod'].nunique()}")
    
    if 'hostname' in clean_df.columns:
        print(f"Host Stars: {clean_df['hostname'].nunique()}")
    
    if 'habitability_score' in clean_df.columns:
        habitable_count = len(clean_df[clean_df['habitability_score'] > 50])
        print(f"Potentially Habitable: {habitable_count}")
    
    if 'disc_year' in clean_df.columns:
        valid_years = clean_df['disc_year'].dropna()
        if len(valid_years) > 0:
            print(f"Date Range: {valid_years.min():.0f} - {valid_years.max():.0f}")
    
    print("=" * 60)
    
    print("\n🎉 All done! You can now use 'exoplanet_data.csv' in your Streamlit app")
    print("\n💡 Next step: Run 'python database_setup.py' to create the database")


if __name__ == "__main__":
    main()
