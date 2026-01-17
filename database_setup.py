"""
Database Setup for Exoplanet Explorer
Creates SQLite database with proper structure and indexes
"""

import sqlite3
import pandas as pd
from datetime import datetime

def create_database(db_name='exoplanets.db'):
    """
    Create SQLite database with optimized structure
    """
    
    print("🗄️  Creating database structure...")
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Table 1: Planets (main data)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS planets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pl_name TEXT UNIQUE NOT NULL,
        hostname TEXT,
        discoverymethod TEXT,
        disc_year INTEGER,
        disc_facility TEXT,
        
        -- Orbital characteristics
        pl_orbper REAL,
        pl_orbsmax REAL,
        
        -- Physical properties
        pl_rade REAL,
        pl_radj REAL,
        pl_masse REAL,
        pl_massj REAL,
        pl_bmasse REAL,
        pl_bmassj REAL,
        pl_bmassprov TEXT,
        pl_dens REAL,
        
        -- Atmospheric properties
        pl_eqt REAL,
        pl_insol REAL,
        
        -- Derived metrics
        habitability_score INTEGER,
        planet_type TEXT,
        discovery_era TEXT,
        distance_category TEXT,
        
        -- Position
        ra REAL,
        dec REAL,
        glat REAL,
        glon REAL,
        
        -- Metadata
        data_fetched_at TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Table 2: Stars (host star information)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT UNIQUE NOT NULL,
        st_teff REAL,
        st_rad REAL,
        st_mass REAL,
        st_met REAL,
        st_logg REAL,
        st_age REAL,
        planet_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Table 3: Systems (planetary system information)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS systems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT UNIQUE NOT NULL,
        sy_snum INTEGER,
        sy_pnum INTEGER,
        sy_dist REAL,
        sy_gaiamag REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_discoverymethod ON planets(discoverymethod)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_disc_year ON planets(disc_year)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hostname ON planets(hostname)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_habitability ON planets(habitability_score)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_planet_type ON planets(planet_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_distance ON systems(sy_dist)')
    
    conn.commit()
    print("   ✓ Database structure created")
    
    return conn


def insert_data_from_csv(conn, csv_file='exoplanet_data.csv'):
    """
    Insert data from CSV into database tables
    """
    
    print("\n📥 Loading data from CSV...")
    df = pd.read_csv(csv_file)
    print(f"   ✓ Loaded {len(df)} records")
    
    cursor = conn.cursor()
    
    # Insert into planets table
    print("\n🪐 Inserting planet data...")
    planets_inserted = 0
    planets_skipped = 0
    
    planet_columns = [
        'pl_name', 'hostname', 'discoverymethod', 'disc_year', 'disc_facility',
        'pl_orbper', 'pl_orbsmax', 'pl_rade', 'pl_radj', 'pl_masse', 'pl_massj',
        'pl_bmasse', 'pl_bmassj', 'pl_bmassprov', 'pl_dens', 'pl_eqt', 'pl_insol',
        'habitability_score', 'planet_type', 'discovery_era', 'distance_category',
        'ra', 'dec', 'glat', 'glon', 'data_fetched_at'
    ]
    
    for _, row in df.iterrows():
        try:
            values = [row.get(col) if pd.notna(row.get(col)) else None for col in planet_columns]
            
            placeholders = ','.join(['?' for _ in planet_columns])
            columns_str = ','.join(planet_columns)
            
            cursor.execute(f'''
                INSERT OR IGNORE INTO planets ({columns_str})
                VALUES ({placeholders})
            ''', values)
            
            if cursor.rowcount > 0:
                planets_inserted += 1
            else:
                planets_skipped += 1
                
        except Exception as e:
            planets_skipped += 1
            continue
    
    print(f"   ✓ Inserted {planets_inserted} planets")
    if planets_skipped > 0:
        print(f"   ℹ️ Skipped {planets_skipped} duplicates")
    
    # Insert into stars table
    print("\n⭐ Inserting star data...")
    star_data = df.groupby('hostname').agg({
        'st_teff': 'first',
        'st_rad': 'first',
        'st_mass': 'first',
        'st_met': 'first',
        'st_logg': 'first',
        'st_age': 'first',
        'pl_name': 'count'
    }).reset_index()
    
    star_data.columns = ['hostname', 'st_teff', 'st_rad', 'st_mass', 'st_met', 
                         'st_logg', 'st_age', 'planet_count']
    
    stars_inserted = 0
    for _, row in star_data.iterrows():
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO stars 
                (hostname, st_teff, st_rad, st_mass, st_met, st_logg, st_age, planet_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['hostname'],
                row['st_teff'] if pd.notna(row['st_teff']) else None,
                row['st_rad'] if pd.notna(row['st_rad']) else None,
                row['st_mass'] if pd.notna(row['st_mass']) else None,
                row['st_met'] if pd.notna(row['st_met']) else None,
                row['st_logg'] if pd.notna(row['st_logg']) else None,
                row['st_age'] if pd.notna(row['st_age']) else None,
                int(row['planet_count'])
            ))
            stars_inserted += 1
        except Exception as e:
            continue
    
    print(f"   ✓ Inserted {stars_inserted} stars")
    
    # Insert into systems table
    print("\n🌌 Inserting system data...")
    system_data = df.groupby('hostname').agg({
        'sy_snum': 'first',
        'sy_pnum': 'first',
        'sy_dist': 'first',
        'sy_gaiamag': 'first'
    }).reset_index()
    
    systems_inserted = 0
    for _, row in system_data.iterrows():
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO systems 
                (hostname, sy_snum, sy_pnum, sy_dist, sy_gaiamag)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['hostname'],
                row['sy_snum'] if pd.notna(row['sy_snum']) else None,
                row['sy_pnum'] if pd.notna(row['sy_pnum']) else None,
                row['sy_dist'] if pd.notna(row['sy_dist']) else None,
                row['sy_gaiamag'] if pd.notna(row['sy_gaiamag']) else None
            ))
            systems_inserted += 1
        except Exception as e:
            continue
    
    print(f"   ✓ Inserted {systems_inserted} systems")
    
    conn.commit()


def verify_database(conn):
    """
    Verify database contents and print statistics
    """
    
    print("\n✅ Verifying database...")
    cursor = conn.cursor()
    
    # Count records in each table
    planet_count = cursor.execute('SELECT COUNT(*) FROM planets').fetchone()[0]
    star_count = cursor.execute('SELECT COUNT(*) FROM stars').fetchone()[0]
    system_count = cursor.execute('SELECT COUNT(*) FROM systems').fetchone()[0]
    
    print(f"   Planets: {planet_count:,}")
    print(f"   Stars: {star_count:,}")
    print(f"   Systems: {system_count:,}")
    
    # Get discovery method stats
    print("\n📊 Top Discovery Methods:")
    methods = cursor.execute('''
        SELECT discoverymethod, COUNT(*) as count
        FROM planets
        WHERE discoverymethod IS NOT NULL
        GROUP BY discoverymethod
        ORDER BY count DESC
        LIMIT 5
    ''').fetchall()
    
    for method, count in methods:
        print(f"   {method}: {count:,}")
    
    # Get habitability stats
    habitable = cursor.execute('''
        SELECT COUNT(*) FROM planets WHERE habitability_score > 50
    ''').fetchone()[0]
    print(f"\n🌍 Potentially Habitable Planets: {habitable}")
    
    # Get year range
    year_range = cursor.execute('''
        SELECT MIN(disc_year), MAX(disc_year) 
        FROM planets 
        WHERE disc_year IS NOT NULL
    ''').fetchone()
    print(f"📅 Discovery Years: {int(year_range[0])} - {int(year_range[1])}")


def main():
    """
    Main execution function
    """
    print("🌌 Exoplanet Database Setup")
    print("=" * 60)
    
    # Create database
    conn = create_database()
    
    # Insert data
    insert_data_from_csv(conn)
    
    # Verify
    verify_database(conn)
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("🎉 Database setup complete!")
    print("   Database file: exoplanets.db")
    print("   Ready to use in Streamlit app!")
    print("=" * 60)


if __name__ == "__main__":
    main()
