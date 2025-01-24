import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from transformers import pipeline
import numpy as np

# Erstelle eine Pipeline für die Sentiment-Analyse
pipe = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment", return_all_scores=True)

with open("processed_data/comments_reddit_bayern.json", "r", encoding="utf-8") as file:
    reddit_comments_bayern = json.loads(file.read())["comments_by_year"]
with open("processed_data/comments_reddit_sh.json", "r", encoding="utf-8") as file:
    reddit_comments_sh = json.loads(file.read())["comments_by_year"]
with open("processed_data/comments_twitter_bayern.json", "r", encoding="utf-8") as file:
    twitter_comments_bayern = json.loads(file.read())["comments_by_year"]
with open("processed_data/comments_twitter_sh.json", "r", encoding="utf-8") as file:
    twitter_comments_sh = json.loads(file.read())["comments_by_year"]


s = "Negative"
title = f"Normalisierter Sentiment-Score bei {s}n Posts"
texts_per_year = reddit_comments_bayern[s] | twitter_comments_bayern[s]

texts_per_year = {key: texts_per_year[key] for key in sorted(texts_per_year)}
# Funktion, um die Sentiment-Werte zu aggregieren und zu normalisieren
def get_sentiment_scores(text):
    result = pipe(text, truncation=True)
    negative_score = result[0][0]['score']
    neutral_score = result[0][1]['score']
    positive_score = result[0][2]['score']
    return negative_score, neutral_score, positive_score

# Funktion zur Aggregation der Sentiment-Werte für jedes Jahr
def aggregate_sentiment_scores(texts):
    aggregated_scores = {'Negative': 0, 'Neutral': 0, 'Positive': 0}

    # Bestimme den höchsten Sentiment-Wert pro Text und addiere ihn
    for text in texts:
        neg, neut, pos = get_sentiment_scores(text)
        # Finde den höchsten Wert des Textes und addiere ihn zur entsprechenden Kategorie
        if neg >= neut and neg >= pos:
            aggregated_scores['Negative'] += 1
        elif neut >= neg and neut >= pos:
            aggregated_scores['Neutral'] += 1
        else:
            aggregated_scores['Positive'] += 1

    return aggregated_scores

# Listen für die Scores über die Jahre hinweg
min_year = 2021
max_year = 2025
years = list(range(min_year, max_year+1, 1))
negative_scores = []
neutral_scores = []
positive_scores = []

# Berechne die Sentiment-Werte für jedes Jahr
for year in years:
    if str(year) not in texts_per_year:
        negative_scores.append(0)
        neutral_scores.append(0)
        positive_scores.append(0)
    else:
        texts = texts_per_year[str(year)]
        year_scores = aggregate_sentiment_scores(texts)

        # Berechne die Gesamtsumme der Scores für das Jahr
        total_score_year = sum(year_scores.values())

        # Normalisiere die Scores für das Jahr
        if total_score_year > 0:
            normalized_negative = year_scores['Negative'] / total_score_year
            normalized_neutral = year_scores['Neutral'] / total_score_year
            normalized_positive = year_scores['Positive'] / total_score_year
        else:
            normalized_negative = normalized_neutral = normalized_positive = 0

        # Füge die normalisierten Werte zu den Listen hinzu
        negative_scores.append(normalized_negative)
        neutral_scores.append(normalized_neutral)
        positive_scores.append(normalized_positive)

# Erstelle das gestapelte Flächendiagramm
plt.figure(figsize=(10, 6))
plt.stackplot(years, negative_scores, neutral_scores, positive_scores,
              labels=['Negative', 'Neutral', 'Positive'],
              colors=['red', 'gray', 'green'], alpha = 0.6)

# Setze Titel und Achsenbeschriftungen
plt.title(title)
plt.xlabel("Year")
plt.ylabel("Normalisierter Sentiment Score")
plt.legend()
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

# Zeige das Diagramm an
plt.show()

# # Gruppiertes Balkendiagramm erstellen
# x = np.arange(len(years))  # Positionen für die Jahre
# width = 0.25  # Breite der Balken

# plt.figure(figsize=(10, 6))
# plt.bar(x - width, negative_scores, width, label='Negative', color='red', alpha=0.7)
# plt.bar(x, neutral_scores, width, label='Neutral', color='gray', alpha=0.7)
# plt.bar(x + width, positive_scores, width, label='Positive', color='green', alpha=0.7)

# # Achsentitel und Beschriftungen hinzufügen
# plt.title(title)
# plt.xlabel("Year")
# plt.ylabel("Normalisierter Sentiment Score")
# plt.xticks(x, [str(year) for year in years])  # Jahre als Beschriftung hinzufügen
# plt.legend()

# # Diagramm anzeigen
# plt.show()