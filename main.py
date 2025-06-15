import os
from itertools import combinations
import multiprocessing as mp
from src.backtesting_engine import run_single_backtest
from src.config import INDICATORS, get_param_combinations
from src.data_preprocessor import process_all_data

def main():
    """Main function to orchestrate the backtesting process."""

    # 1. Pre-process data to ensure it's up to date
    print("--- Starting Data Pre-processing ---")
    process_all_data()
    print("--- Data Pre-processing Finished ---")

    # 2. Get list of companies from processed data
    processed_dir = 'data/processed'
    if not os.path.exists(processed_dir) or not os.listdir(processed_dir):
        print("No processed data found. Please add raw CSV data to 'data/raw' and run again.")
        return
        
    companies = [f.split('.')[0] for f in os.listdir(processed_dir) if f.endswith('.parquet')]
    indicator_names = list(INDICATORS.keys())
    indicator_pairs = list(combinations(indicator_names, 2))

    tasks = []
    
    # 3. Create a list of all backtesting tasks
    print("--- Generating Backtest Tasks ---")
    for company in companies:
        for ind1_name, ind2_name in indicator_pairs:
            params1_list = list(get_param_combinations(ind1_name))
            params2_list = list(get_param_combinations(ind2_name))
            
            # Create a task for each combination of parameters
            for p1 in params1_list:
                for p2 in params2_list:
                    # Avoid backtesting an indicator against itself if it has no params
                    if ind1_name == ind2_name and p1 == p2:
                        continue
                    tasks.append((company, (ind1_name, ind2_name), p1, p2))

    if not tasks:
        print("No tasks generated. Check your config.py for parameter grids.")
        return

    print(f"Total tasks to run: {len(tasks)}")
    
    # 4. Run tasks in parallel using a process pool
    # Use one less than the total number of CPU cores to keep the system responsive
    num_processes = max(1, mp.cpu_count() - 1)
    print(f"--- Starting Backtests on {num_processes} cores ---")
    
    with mp.Pool(processes=num_processes) as pool:
        # Use imap_unordered for better progress visibility
        for i, result in enumerate(pool.imap_unordered(run_single_backtest, tasks), 1):
            # Print progress and any errors
            print(f"Progress: {i}/{len(tasks)} -> {result}")

    print("--- All Backtests Finished ---")
    print("Reports have been saved to the /reports directory.")

if __name__ == '__main__':
    main()
