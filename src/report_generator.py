import os
import math

def generate_html_report(company, ind1_name, ind2_name, params1, params2, final_value, pnl, trades, sharpe, max_dd):
    """Generates and saves a single HTML report for a backtest run."""
    
    # Create a clean string for filenames
    p1_str = '_'.join(map(str, params1.values())) if params1 else "default"
    p2_str = '_'.join(map(str, params2.values())) if params2 else "default"
    
    # Create directories if they don't exist
    report_dir = f'reports/{company}/'
    os.makedirs(report_dir, exist_ok=True)
    
    filename = f"{report_dir}report_{ind1_name}_{p1_str}_{ind2_name}_{p2_str}.html"

    # --- Extract and clean metrics from TradeAnalyzer ---
    total_trades = trades.total.total if trades and trades.total else 0
    wins = trades.won.total if trades and trades.won else 0
    losses = trades.lost.total if trades and trades.lost else 0
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    # Clean up potential None or NaN values for display
    sharpe_display = f"{sharpe:.3f}" if sharpe and not math.isnan(sharpe) else 'N/A'
    pnl_display = f"{pnl:,.2f}" if pnl and not math.isnan(pnl) else 'N/A'
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Backtest Report: {company}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 2em; background-color: #f8f9fa; color: #212529; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 2em; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            h1, h2 {{ color: #0056b3; border-bottom: 2px solid #dee2e6; padding-bottom: 0.3em; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 1.5em; }}
            th, td {{ border: 1px solid #dee2e6; padding: 12px; text-align: left; }}
            th {{ background-color: #e9ecef; font-weight: 600; }}
            tr:nth-child(even) {{ background-color: #f8f9fa; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Backtest Report</h1>
            <h2>Configuration</h2>
            <table>
                <tr><th>Company</th><td>{company}</td></tr>
                <tr><th>Indicator 1</th><td>{ind1_name} (Params: {params1 or 'Default'})</td></tr>
                <tr><th>Indicator 2</th><td>{ind2_name} (Params: {params2 or 'Default'})</td></tr>
            </table>

            <h2>Performance Summary</h2>
            <table>
                <tr><th>Net Profit/Loss (PNL)</th><td>{pnl_display}</td></tr>
                <tr><th>Final Portfolio Value</th><td>{final_value:,.2f}</td></tr>
                <tr><th>Sharpe Ratio (Annualized)</th><td>{sharpe_display}</td></tr>
                <tr><th>Max Drawdown (%)</th><td>{max_dd:.2f}</td></tr>
                <tr><th>Total Trades</th><td>{total_trades}</td></tr>
                <tr><th>Winning Trades</th><td>{wins}</td></tr>
                <tr><th>Losing Trades</th><td>{losses}</td></tr>
                <tr><th>Win Rate (%)</th><td>{win_rate:.2f}</td></tr>
            </table>
        </div>
    </body>
    </html>
    """

    with open(filename, 'w') as f:
        f.write(html)