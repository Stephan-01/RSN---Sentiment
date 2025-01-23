import matplotlib.pyplot as plt
from transformers import pipeline
import numpy as np

# Erstelle eine Pipeline für die Sentiment-Analyse
pipe = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment", return_all_scores=True)

# Beispieltexte, die über die Jahre verteilt sind
texts_per_year = {
    'Year 2020': [
        "Windkraft ist das beste was es gibt",

    ],
    'Year 2021': [
        "Windkraft ist müll",
        "Ich stimme dir nicht zu"
    ],
    'Year 2022': [
        "Windkraft ist gut für die Umwelt",
        "Ich bin nicht überzeugt von Windkraft"
    ],
    'Year 2023': [
        "Ich finde Windkraft nicht nachhaltig",
        "Windkraft ist eine gute Energiequelle"
    ],
    'Year 2024': [
        "Windkraft ist immer noch aktuell",
        "Ich unterstütze Windkraft voll und ganz"
    ],
    'Year 2025': [
        "Die Natur wird durch Windkraft zerstört",
        "Windkraft ist eine der besten Lösungen"
    ]
}

# Funktion, um die Sentiment-Werte zu aggregieren und zu normalisieren
def get_sentiment_scores(text):
    result = pipe(text)
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
years = list(texts_per_year.keys())
negative_scores = []
neutral_scores = []
positive_scores = []

# Berechne die Sentiment-Werte für jedes Jahr
for year, texts in texts_per_year.items():
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
plt.title("Normalized Sentiment Over Time (2020-2025)")
plt.xlabel("Year")
plt.ylabel("Normalized Sentiment Score")
plt.legend()

# Zeige das Diagramm an
plt.show()

# Gruppiertes Balkendiagramm erstellen
x = np.arange(len(years))  # Positionen für die Jahre
width = 0.25  # Breite der Balken

plt.figure(figsize=(10, 6))
plt.bar(x - width, negative_scores, width, label='Negative', color='red', alpha=0.7)
plt.bar(x, neutral_scores, width, label='Neutral', color='gray', alpha=0.7)
plt.bar(x + width, positive_scores, width, label='Positive', color='green', alpha=0.7)

# Achsentitel und Beschriftungen hinzufügen
plt.title("Sentiment Analysis per Year (2020-2025)")
plt.xlabel("Year")
plt.ylabel("Normalized Sentiment Score")
plt.xticks(x, years)  # Jahre als Beschriftung hinzufügen
plt.legend()

# Diagramm anzeigen
plt.show()