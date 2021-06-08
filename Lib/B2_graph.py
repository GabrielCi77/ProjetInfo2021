import pandas as pd
import matplotlib.pyplot as plt
import B1_first as f

# Prix
df_spot_eur = pd.read_csv('../Data/SpotEur.csv', index_col='Date')
df_spot_eur.index = pd.to_datetime(df_spot_eur.index)

df_spot_us = pd.read_csv('../Data/SpotUS.csv', index_col='Date')
df_spot_us.index = pd.to_datetime(df_spot_us.index)

df_prices = pd.merge(df_spot_eur, df_spot_us, on='Date')
df_spot_eur.plot()
df_spot_us.plot()
df_prices.plot()

# Histogramme
df_trips = f.loadTripsAndPriceData()
df_trips = df_trips[(df_trips['Dcountry'].isin(f.producers)) & (df_trips['A_EU'] + df_trips['A_AS'] == 1)]
df_trips.set_index(['Dcountry', pd.to_datetime(df_trips['Atime'])], inplace=True)
df_trips = df_trips[['A_EU', 'A_AS']]

dfg = df_trips.groupby([pd.Grouper(level='Dcountry'), pd.Grouper(level='Atime', freq='2W')]).sum()
print(dfg)
ax = dfg.loc[' United States (USA)'].plot()  # .bar(stacked=True)
df_spot_eur.plot(ax=ax)
plt.show()
