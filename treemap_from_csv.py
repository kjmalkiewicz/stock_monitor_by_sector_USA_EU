
import pandas as pd
import yfinance as yf
import plotly.express as px

# Wczytaj tickery europejskie i USA (S&P 500)
print("🔽 Wczytywanie tickerów z CSV...")
df_eu = pd.read_csv("europe_tickers.csv")
df_us = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
df_us = pd.DataFrame({
    "Ticker": df_us["Symbol"],
    "Region": "USA"
})

df_all = pd.concat([df_us, df_eu], ignore_index=True)
df_all = df_all[~df_all["Ticker"].isin(["GOOG"])]

# Pobierz dane z yfinance
print("📡 Pobieranie danych z yfinance...")
records = []
for _, row in df_all.iterrows():
    ticker = row["Ticker"]
    region = row["Region"]
    try:
        info = yf.Ticker(ticker).info
        sector = info.get("sector")
        market_cap = info.get("marketCap")
        if sector and market_cap:
            records.append({
                "Ticker": ticker,
                "Company": info.get("shortName", ticker),
                "Sector": sector,
                "MarketCap": market_cap / 1e9,
                "Region": region
            })
    except Exception:
        continue

df_info = pd.DataFrame(records)
print(f"✅ Zebrano dane dla {len(df_info)} spółek.")

# Wybierz Top 5 z każdego sektora
def top5_by_sector(df):
    return df.groupby("Sector", group_keys=False).apply(lambda g: g.nlargest(5, "MarketCap"))

df_usa = top5_by_sector(df_info[df_info["Region"] == "USA"])
df_europe = top5_by_sector(df_info[df_info["Region"] == "Europe"])

# Wygeneruj wykresy
fig_usa = px.treemap(df_usa, path=["Sector", "Company"], values="MarketCap", title="Top 5 spółek wg sektora – USA")
fig_europe = px.treemap(df_europe, path=["Sector", "Company"], values="MarketCap", title="Top 5 spółek wg sektora – Europa")

fig_usa.write_html("usa.html")
fig_europe.write_html("europe.html")

# Ładny HTML
with open("combined_treemap.html", "w", encoding="utf-8") as f:
    f.write(f"""
<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <title>Top 5 spółek wg sektora</title>
  <style>
    body {{ font-family: Arial; background: #f4f4f4; padding: 40px; }}
    h1 {{ text-align: center; }}
    iframe {{ border: none; width: 100%; height: 600px; margin-bottom: 50px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
  </style>
</head>
<body>
  <h1>Top 5 spółek wg sektora</h1>
  <iframe src="usa.html"></iframe>
  <iframe src="europe.html"></iframe>
</body>
</html>
""")

print("✅ Zakończono: combined_treemap.html")
