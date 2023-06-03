import os
import pandas as pd

def vbt_saver_printer(
    strategy_class: str, 
    strategy_config: str,
    stats_df: pd.DataFrame,
    position_df: pd.DataFrame,
    bt_df: pd.DataFrame,
    vbt_func, 
    asset_return: pd.DataFrame,
    asset_value: pd.DataFrame,
    cumulative_returns: pd.DataFrame
):
    
    save_dir = f'{os.path.dirname(__file__)}/backtest_result'
    os.makedirs(save_dir, exist_ok=True)

    stats_dir = f"{save_dir}/{strategy_class}/stats/{strategy_config}"
    os.makedirs(stats_dir, exist_ok=True)
    position_dir = f"{save_dir}/{strategy_class}/position/{strategy_config}"
    os.makedirs(position_dir, exist_ok=True)
    metric_df_dir = f"{save_dir}/{strategy_class}/metric_df/{strategy_config}"
    os.makedirs(metric_df_dir, exist_ok=True)
    asset_dir = f"{save_dir}/{strategy_class}/asset/{strategy_config}"
    os.makedirs(asset_dir, exist_ok=True)
    trade_pnl_dir = f"{save_dir}/{strategy_class}/trade_pnl/{strategy_config}"
    os.makedirs(trade_pnl_dir, exist_ok=True)

    # Saving dataframes
    stats_df.to_csv(f"{stats_dir}/{strategy_config}_stats_vbt.csv")
    position_df.to_csv(f"{position_dir}/{strategy_config}_position_vbt.csv")
    bt_df.to_csv(f"{metric_df_dir}/{strategy_config}_metric_df_vbt.csv")
    trade_record = vbt_func.positions.records_readable
    trade_record.to_csv(f"{trade_pnl_dir}/{strategy_config}_trade_pnl_vbt.csv")
    asset_return.to_csv(f"{asset_dir}/{strategy_config}_asset_return_vbt.csv")
    asset_value.to_csv(f"{asset_dir}/{strategy_config}_asset_value_vbt.csv")
    cumulative_returns.to_csv(f"{asset_dir}/{strategy_config}_cumulative_returns_vbt.csv")

    print("VBT Backtest Report Saved Success!")
