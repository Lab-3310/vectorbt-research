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
    
    save_dir = f'{os.path.dirname(__file__)}/../backtest_result/{strategy_class}/{strategy_config}'
    os.makedirs(save_dir, exist_ok=True)

    # Saving dataframes to local file
    stats_df.to_csv(f'{save_dir}/{strategy_config}_stats_vbt.csv')
    position_df.to_csv(f'{save_dir}/{strategy_config}_position_vbt.csv')
    bt_df.to_csv(f'{save_dir}/{strategy_config}_metric_df_vbt.csv')

    asset_return.to_csv(f'{save_dir}/{strategy_config}_asset_return_vbt.csv')
    asset_value.to_csv(f'{save_dir}/{strategy_config}_asset_value_vbt.csv')
    cumulative_returns.to_csv(f'{save_dir}/{strategy_config}_cumulative_returns_vbt.csv')

    trade_record = vbt_func.positions.records_readable
    trade_record.to_csv(f'{save_dir}/{strategy_config}_trade_pnl_vbt.csv')
    print('Backtest Results')
    print('---------')
    print(stats_df)
    print('---------')

    print(f'VBT Backtest Report in {strategy_class}/{strategy_config} Saved Success!')
