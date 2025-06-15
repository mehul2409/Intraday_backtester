# High-Performance Intraday Backtesting Framework

This project is a high-performance backtesting engine designed to test pairs of technical indicators against historical intraday stock data. It uses `polars` for efficient data manipulation and `multiprocessing` to run thousands of backtests in parallel.

---

## Folder Structure

The project is organized into a modular structure to keep data, source code, and reports separate and manageable.


/intraday_backtester/
    
    -- data/
        -- raw/
        -- processed/

    -- reports/

    -- src/
         -- init.py
         -- config.py
         -- custom_indicators.py
         -- data_preprocessor.py
         -- backtesting_engine.py
         -- report_generator.py
    -- main.py
    -- requirements.txt
    -- create_sample_data.py
    -- README.md


---

### Directory and File Descriptions

* `data/`: Contains all market data.
    * `raw/`: Place your raw, original `.csv` files for each stock here. The data pre-processor reads from this directory.
    * `processed/`: The pre-processor saves cleaned, optimized `.parquet` files here. The backtesting engine reads from this directory for high performance.

* `reports/`: All generated HTML backtest reports are saved here. The script automatically creates a sub-directory for each company symbol.

* `src/`: Contains all the core application logic.
    * `__init__.py`: Makes the `src` directory a Python package.
    * `config.py`: The central configuration hub. Define all indicators, their parameter ranges (`PARAM_GRID`), and other settings here.
    * `custom_indicators.py`: Contains Python classes for any indicators that are not included by default in the `backtrader` library (e.g., `SuperTrend`, `OnBalanceVolume`). This makes the framework more robust.
    * `data_preprocessor.py`: A script to read raw CSV files, clean them, and save them in the efficient Parquet format.
    * `backtesting_engine.py`: The core of the application. It contains the `DualIndicatorStrategy`, the `PolarsDataFeed`, and the `run_single_backtest` worker function for multiprocessing.
    * `report_generator.py`: A dedicated module for creating the final HTML reports from the backtest results.

* `main.py`: The main entry point to execute the entire backtesting suite. It orchestrates the data pre-processing and distributes the backtesting tasks to the engine.

* `requirements.txt`: Lists all the necessary Python libraries for the project.

* `create_sample_data.py`: An optional utility script to generate a sample data file (`SAMPLE.csv`) for testing the framework without needing real data.

* `README.md`: This file. It provides an overview and instructions for the project.

---

### How to Run

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Add Data**: Place your `.csv` files into the `data/raw/` folder. The CSVs must contain `Date`, `Open`, `High`, `Low`, `Close`, and `Volume` columns.

3.  **Run the Backtester**: Execute the main script from the root directory.
    ```bash
    python main.py
    ```

    The script will automatically process the data and run all backtest combinations defined in `src/config.py`.

### Customization

* **To run a small test**, edit `main.py` to limit the `companies` and `indicator_pairs` lists. You can also reduce the parameter ranges in the `PARAM_GRID` dictionary in `src/config.py`.
* **To add a new indicator**, add it to the `INDICATORS` dictionary in `src/config.py`. If it's not a standard `backtrader` indicator, you must first implement it in `src/custom_indicators.py`.

