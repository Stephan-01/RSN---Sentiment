import matplotlib.pyplot as plt
from transformers import pipeline

# Erstelle eine Pipeline für die Sentiment-Analyse
pipe = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment", return_all_scores=True)

# Beispieltexte für verschiedene soziale Netzwerke
texts = {
    'Instagram': [
        "ich bin deiner meinung",
        "ich bin neutral",
        "ich stimme nicht zu"
    ],
    'Reddit': [
        "du hast keine Ahnung",
        "ich bin generell gegen Windkraft",
        "ich stimme dir zu"
    ]
}

# Funktion zur Aggregation der höchsten Sentiment-Werte
def aggregate_max_sentiment(texts):
    aggregated_scores = {'Negative': 0, 'Neutral': 0, 'Positive': 0}

    # Aggregiere den höchsten Sentiment-Wert für alle Texte
    for text in texts:
        result = pipe(text)
        # Hole den höchsten Score und den entsprechenden Sentiment-Typ
        max_score = max(result[0][0]['score'], result[0][1]['score'], result[0][2]['score'])

        # Bestimme, welches Sentiment der höchste Score war
        if max_score == result[0][0]['score']:
            aggregated_scores['Negative'] += max_score
        elif max_score == result[0][1]['score']:
            aggregated_scores['Neutral'] += max_score
        else:
            aggregated_scores['Positive'] += max_score

    return aggregated_scores

# Aggregiere die höchsten Sentiment-Werte für jedes Netzwerk
aggregated_scores_instagram = aggregate_max_sentiment(texts['Instagram'])
aggregated_scores_reddit = aggregate_max_sentiment(texts['Reddit'])

# Berechne die Gesamtzahl der Scores für Normalisierung
total_score_instagram = sum(aggregated_scores_instagram.values())
total_score_reddit = sum(aggregated_scores_reddit.values())

# Normalisiere die Scores, indem wir jeden Wert durch die Gesamtsumme teilen
if total_score_instagram > 0:  # Vermeiden einer Division durch Null
    normalized_scores_instagram = {key: score / total_score_instagram for key, score in aggregated_scores_instagram.items()}
else:
    normalized_scores_instagram = aggregated_scores_instagram

if total_score_reddit > 0:
    normalized_scores_reddit = {key: score / total_score_reddit for key, score in aggregated_scores_reddit.items()}
else:
    normalized_scores_reddit = aggregated_scores_reddit

# Listen der normalisierten Scores für jedes Netzwerk
scores_instagram = [normalized_scores_instagram['Negative'], normalized_scores_instagram['Neutral'], normalized_scores_instagram['Positive']]
scores_reddit = [normalized_scores_reddit['Negative'], normalized_scores_reddit['Neutral'], normalized_scores_reddit['Positive']]

# Sentiments (Negative, Neutral, Positive)
sentiments = ['Negative', 'Neutral', 'Positive']

# Farben für die Sentiments
colors = ['red', 'gray', 'green']

# Erstelle das gestapelte Balkendiagramm
fig, ax = plt.subplots(figsize=(10, 6))

# Staple die normalisierten Balken für Instagram und Reddit
ax.bar('Instagram', scores_instagram[0], color='red', bottom=0)
ax.bar('Instagram', scores_instagram[1], color='gray', bottom=scores_instagram[0])
ax.bar('Instagram', scores_instagram[2], color='green', bottom=scores_instagram[0] + scores_instagram[1])

ax.bar('Reddit', scores_reddit[0], color='red', bottom=0)
ax.bar('Reddit', scores_reddit[1], color='gray', bottom=scores_reddit[0])
ax.bar('Reddit', scores_reddit[2], color='green', bottom=scores_reddit[0] + scores_reddit[1])

# Setze Titel und Achsenbeschriftungen
ax.set_title("Normalized Sentiment Analysis Results for Social Networks")
ax.set_xlabel("Social Network")
ax.set_ylabel("Normalized Sentiment Score")

# Zeige nur eine Legende für die Sentiments an (nicht doppelt)
ax.legend(['Negative', 'Neutral', 'Positive'], loc='upper left')

# Zeige das Diagramm an
plt.show()
