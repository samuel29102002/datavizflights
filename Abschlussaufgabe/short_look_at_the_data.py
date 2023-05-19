###-------------Nicht für die Bewertung beachten!!!!--------------###
import pandas as pd
from plotly.subplots import make_subplots
import requests
import io

#df = pd.read_csv('/Users/samuel/DS101_DV/data/airlines.csv', sep=';')

csv_url = 'https://gist.githubusercontent.com/florianeichin/cfa1705e12ebd75ff4c321427126ccee/raw/c86301a0e5d0c1757d325424b8deec04cc5c5ca9/flights_all_cleaned.csv'
csv_data = requests.get(csv_url).content
df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')), sep=',')
print(df.head())


print(df['AIRLINE'].value_counts(dropna=False))
print('- - - Head - - -')
print(df.head(10))

print('\n- - - Shape - - -')
print(df.shape)

print('\n- - - Mean - - -')
print(df.mean(numeric_only=True))

print('\n- - - Median - - -')
print(df.median(numeric_only=True))

print('\n- - - Count - - -')
print(df.count())

print('\n- - - Max - - -')
print(df.max(numeric_only=True))

print('\n- - - Min - - -')
print(df.min(numeric_only=True))

print('\n- - - Correlation - - -')
print(df.corr())

print('\n- - - Standard Deviation - - -')
print(df.std(numeric_only=True))

print('###-------------Nicht für die Bewertung beachten!!!!--------------###')
