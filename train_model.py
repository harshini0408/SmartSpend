from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# Expanded and corrected training data
expenses = [
    "milk", "bread", "rice", "fruits", "vegetables", "chicken", "coffee", "tea", "eggs", "butter",
    "electricity bill", "water bill", "gas bill", "internet", "phone recharge", "cable tv", "streaming service",
    "bus ticket", "train ticket", "petrol", "uber", "auto rickshaw", "taxi", "flight ticket",
    "restaurant", "fast food", "pizza", "burger", "sandwich", "sushi", "cafe", "bar", "alcohol",
    "t-shirt", "jeans", "shoes", "dress", "jacket", "socks", "underwear", "hat", "watch", "jewelry",
    "notebook", "pencil", "pen", "eraser", "calculator", "stapler", "printer ink", "paper", "folder",
    "hospital", "medicine", "doctor consultation", "health checkup", "pharmacy", "vitamins", "gym membership",
    "movie ticket", "concert", "netflix", "spotify", "amazon prime", "video game", "book", "magazine",
    "rent", "mortgage", "loan payment", "insurance", "property tax", "home maintenance", "furniture"
]

categories = [
    "Groceries", "Groceries", "Groceries", "Groceries", "Groceries", "Groceries", "Groceries", "Groceries", "Groceries", "Groceries",
    "Utilities", "Utilities", "Utilities", "Utilities", "Utilities", "Utilities", "Utilities",
    "Transportation", "Transportation", "Transportation", "Transportation", "Transportation", "Transportation", "Transportation",
    "Food", "Food", "Food", "Food", "Food", "Food", "Food", "Food", "Food",
    "Shopping", "Shopping", "Shopping", "Shopping", "Shopping", "Shopping", "Shopping", "Shopping", "Shopping", "Shopping",
    "Stationery", "Stationery", "Stationery", "Stationery", "Stationery", "Stationery", "Stationery", "Stationery", "Stationery",
    "Medical", "Medical", "Medical", "Medical", "Medical", "Medical", "Medical",
    "Entertainment", "Entertainment", "Entertainment", "Entertainment", "Entertainment", "Entertainment", "Entertainment", "Entertainment",
    "Housing", "Housing", "Housing", "Housing", "Housing", "Housing", "Housing"
]

# Train the model
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(expenses)
model = LogisticRegression()
model.fit(X, categories)

# Save the model and vectorizer
joblib.dump(model, 'expense_category_model.pkl')
joblib.dump(vectorizer, 'expense_category_vectorizer.pkl')

print("Updated model trained and saved successfully!")