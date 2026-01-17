import pandas as pd

def clean_exoplanet_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and preprocesses raw exoplanet data
    from NASA Exoplanet Archive.
    """

    # Drop duplicate planets
    df = df.drop_duplicates(subset="pl_name")

    # Convert discovery year to integer
    df["disc_year"] = pd.to_numeric(df["disc_year"], errors="coerce")

    # Remove rows with missing critical values
    df = df.dropna(subset=["pl_rade", "pl_eqt", "pl_orbper"])

    # Ensure numeric columns
    numeric_cols = [
        "pl_rade",
        "pl_eqt",
        "pl_orbper",
        "st_teff",
        "st_rad"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
