"""read_data.py
Module to read and process the catalog of products.
"""
import pandas as pd
def read_data() -> pd.DataFrame:
    """Reads and processes clothing catalog data set.

    Returns:
        pd.DataFrame: Catalog data.
    """
    data = pd.read_csv(f"data/catalog_subset.csv")
    data.columns = data.columns.str.lower()
    data = data.rename(columns = {"total revenue (coins)": "revenue", "time (hrs)": "duration",
                                  "price (coins)": "cost", "experience (xp)": "xp"})
    data["benefit"] = data["revenue"] - data["cost"]
    data = data[data["duration"] >= 1] # Only products with at least 1 hour duration are relevant
    data["id"] = list(range(len(data)))
    return data
