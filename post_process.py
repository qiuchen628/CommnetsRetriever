import pandas as pd

df = pd.read_csv("/Users/chenqiu/PycharmProjects/youtube_crawl/comments.csv")
print(df.head(5))



print(df['Video ID'])

print("******************")
ids = len(set(list(df['Video ID'])))
print(set(list(df['Video ID'])))
print(ids)