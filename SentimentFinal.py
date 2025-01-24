import json
import matplotlib.pyplot as plt
import tqdm
from transformers import pipeline
from unidecode import unidecode

# Erstelle eine Pipeline für die Sentiment-Analyse

pipe = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis", return_all_scores=True)
# pipe = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment", return_all_scores=True)


with open("processed_data/comments_twitter_bayern.json", "r", encoding="utf-8") as file:
    twitter_comments_bayern = json.loads(file.read())
with open("processed_data/comments_twitter_sh.json", "r", encoding="utf-8") as file:
    twitter_comments_sh = json.loads(file.read())

with open("processed_data/comments_reddit_bayern.json", "r", encoding="utf-8") as file:
    reddit_comments_bayern = json.loads(file.read())
with open("processed_data/comments_reddit_sh.json", "r", encoding="utf-8") as file:
    reddit_comments_sh = json.loads(file.read())

with open("processed_data/comments_youtube_bayern.json", "r", encoding="utf-8") as file:
    youtube_comments_bayern = json.loads(file.read())
with open("processed_data/comments_youtube_sh.json", "r", encoding="utf-8") as file:
    youtube_comments_sh = json.loads(file.read())



# Beispieltexte für verschiedene soziale Netzwerke
title = "Vergleich Sentiment der Kommentare"
# label_one = "Kommentare auf positive Posts"
# label_two = "Kommentare auf negative Posts"
label_three = "Kommentare Bayern"
label_four = "Kommentare SH"

texts = {
    # label_one: reddit_comments_sh["comments_on_positive_posts"],
    # label_two: reddit_comments_sh["comments_on_negative_posts"],
    label_three: youtube_comments_bayern["comments_on_posts"],
    label_four: youtube_comments_sh["comments_on_posts"]
}

# Funktion zur Aggregation der höchsten Sentiment-Kategorien
def aggregate_max_sentiment(texts):
    aggregated_scores = {'Negative': 0, 'Neutral': 0, 'Positive': 0}

    # Aggregiere den höchsten Sentiment-Wert für alle Texte
    for text in tqdm.tqdm(texts):
        result = pipe(text, truncation=True)
        # Hole den höchsten Score und den entsprechenden Sentiment-Typ
        max_score_category = max(result[0], key=lambda x: x['score'])['label'] # type: ignore

        # Erhöhe den Zähler für das entsprechende Sentiment
        if max_score_category == "Neutral":
            aggregated_scores['Neutral'] += 1
        elif max_score_category == "Positive" or max_score_category == "Very Positive":
            aggregated_scores['Positive'] += 1
        elif max_score_category == "Negative" or max_score_category == "Very Negative":
            aggregated_scores['Negative'] += 1

    print(aggregated_scores)
    return aggregated_scores



# Erstelle das gestapelte Balkendiagramm
fig, ax = plt.subplots(figsize=(10, 6))

for label in texts:
    # Aggregiere die höchsten Sentiment-Werte für jedes Netzwerk
    aggregated_scores_label = aggregate_max_sentiment(texts[label])
    # Berechne die Gesamtzahl der Scores für Normalisierung
    total_score_label = sum(aggregated_scores_label.values())
    # Normalisiere die Scores, indem wir jeden Wert durch die Gesamtsumme teilen
    if total_score_label > 0:  # Vermeiden einer Division durch Null
        normalized_scores_label = {key: score / total_score_label for key, score in aggregated_scores_label.items()}
    else:
        normalized_scores_label = aggregated_scores_label
    # Listen der normalisierten Scores für jedes Netzwerk
    scores_label = [normalized_scores_label['Negative'], normalized_scores_label['Neutral'], normalized_scores_label['Positive']]

    # Staple die normalisierten Balken für Instagram und Reddit
    ax.bar(label, scores_label[0], color='red', bottom=0, alpha = 0.6)
    ax.bar(label, scores_label[1], color='gray', bottom=scores_label[0], alpha = 0.6)
    ax.bar(label, scores_label[2], color='green', bottom=scores_label[0] + scores_label[1], alpha = 0.6)


# Sentiments (Negative, Neutral, Positive)
sentiments = ['Negative', 'Neutral', 'Positive']

# Farben für die Sentiments
colors = ['red', 'gray', 'green']


# Setze Titel und Achsenbeschriftungen
ax.set_title(title)
# ax.set_xlabel("Social Network")
ax.set_ylabel("Normalisierter Sentiment Score")

# Zeige nur eine Legende für die Sentiments an (nicht doppelt)
ax.legend(['Negativ', 'Neutral', 'Positiv'], loc='upper left')

# Zeige das Diagramm an
plt.show()
