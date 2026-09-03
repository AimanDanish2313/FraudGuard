import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

nltk.download('stopwords', quiet=True)

# 1. Preprocessing Function (Module A)
def preprocess_text(text):
    cleaned_text = re.sub("[^a-zA-Z]", " ", text)
    words = cleaned_text.lower().split()
    ps = PorterStemmer()
    stop_words = set(stopwords.words("english"))
    return " ".join([ps.stem(word) for word in words if word not in stop_words])

# Sample Dataset for Training (Module B & C)
raw_reviews = [
    "This restaurant is absolutely amazing! I loved the food.",
    "Terrible service and awful food. Never coming back.",
    "Great place, awesome ambiance, highly recommended!",
    "The worst experience ever, dirty table and cold meal.",
    "Delicious food, friendly staff, five stars!",
    "Horrible experience, slow service and overpriced.",
    "Fantastic taste and excellent quality overall.",
    "Disgusting food and extremely rude waiter."
] * 10  # Duplicate dataset size

labels = [1, 0, 1, 0, 1, 0, 1, 0] * 10  # 1 = Positive, 0 = Negative

# Preprocess Corpus
corpus = [preprocess_text(r) for r in raw_reviews]

# 2. Feature Extraction (Module B)
bow = CountVectorizer(max_features=1500)
X_bow = bow.fit_transform(corpus).toarray()

tfidf = TfidfVectorizer(max_features=1500)
X_tfidf = tfidf.fit_transform(corpus).toarray()

# 3. Model Training & Evaluation (Module C)
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, labels, test_size=0.2, random_state=0)

# Naive Bayes
nb = MultinomialNB()
nb.fit(X_train, y_train)
y_pred_nb = nb.predict(X_test)

# SVM
svm = SVC(kernel="linear")
svm.fit(X_train, y_train)
y_pred_svm = svm.predict(X_test)

print("--- MODEL PERFORMANCE ---")
print(f"Naive Bayes Accuracy: {accuracy_score(y_test, y_pred_nb):.4f}")
print(f"SVM Accuracy:         {accuracy_score(y_test, y_pred_svm):.4f}\n")

# 4. Inference on New Data (Module D)
new_reviews = [
    "This restaurant is amazing, I love the food!",
    "Terrible service, will never come back.",
    "The food was okay, nothing special.",
    "Best pizza I have ever had!",
    "Worst experience of my life."
]

print("--- NEW PREDICTIONS ---")
for r in new_reviews:
    p_text = preprocess_text(r)
    vec = tfidf.transform([p_text]).toarray()  # Matrix converted to array for dense SVM compatibility
    pred = svm.predict(vec)[0]
    sentiment = "Positive" if pred == 1 else "Negative"
    print(f"Review: '{r}' --> {sentiment}")