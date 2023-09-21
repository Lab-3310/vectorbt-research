# import 


# Jason 
fast_ma, slow_ma = vbt.MA.run_combs(in_sample_prices(28, 360, 108), window=np.arange(1, 25), r=2, short_names=['fast', 'slow'])

entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

pf = vbt.Portfolio.from_signals(in_sample_prices(28, 360, 108), entries, exits)
res = pf.total_return()

get_optimal(res)