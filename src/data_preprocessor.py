import polars as pl
import os

RAW_DATA_DIR = 'data/raw/'
PROCESSED_DATA_DIR = 'data/processed/'

def process_all_data():
    """Converts all raw CSV files to cleaned Parquet files."""
    if not os.path.exists(PROCESSED_DATA_DIR):
        os.makedirs(PROCESSED_DATA_DIR)

    for filename in os.listdir(RAW_DATA_DIR):
        if filename.endswith('.csv'):
            company_symbol = filename.split('.')[0]
            csv_path = os.path.join(RAW_DATA_DIR, filename)
            
            try:
                # Read and process data with Polars
                df = pl.read_csv(csv_path)

                # Standardize column names
                rename_map = {col: col.lower() for col in df.columns}
                df = df.rename(rename_map)

                # Ensure backtrader compatible names
                df = df.rename({
                    'date': 'datetime',  # Common alternative name
                })

                # Convert datetime string to actual datetime objects
                # This tries to automatically parse common date formats
                df = df.with_columns(
                    pl.col('datetime').str.to_datetime().alias('datetime')
                )

                # Handle potential missing values
                df = df.drop_nulls()

                # Ensure data is sorted by time
                df = df.sort('datetime')
                
                # Check for required columns
                required_cols = {'datetime', 'open', 'high', 'low', 'close', 'volume'}
                if not required_cols.issubset(df.columns):
                    print(f"Skipping {filename}: Missing one of the required columns (datetime, open, high, low, close, volume)")
                    continue

                # Save to a fast, efficient format
                parquet_path = os.path.join(PROCESSED_DATA_DIR, f"{company_symbol}.parquet")
                df.write_parquet(parquet_path)
                print(f"Processed and saved data for {company_symbol}")

            except Exception as e:
                print(f"Could not process {filename}. Error: {e}")

if __name__ == '__main__':
    process_all_data()
