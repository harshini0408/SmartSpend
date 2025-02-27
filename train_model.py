from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# Expanded and corrected training data with more categories
expenses = [
    # Groceries (15 items)
    "milk", "bread", "rice", "fruits", "vegetables", "chicken", "coffee", "tea", "eggs", "butter",
    "cheese", "cereal", "yogurt", "snacks", "chocolate",
    
    # Utilities (9 items)
    "electricity bill", "water bill", "gas bill", "internet", "phone recharge", "cable tv", "streaming service",
    "waste management", "solar energy",

    # Transportation (10 items)
    "bus ticket", "train ticket", "petrol", "uber", "auto rickshaw", "taxi", "flight ticket",
    "bicycle rental", "metro pass", "car maintenance",

    # Food & Dining (14 items)
    "restaurant", "fast food", "pizza", "burger", "sandwich", "sushi", "cafe", "bar", "alcohol",
    "ice cream", "bakery", "buffet", "fine dining", "street food",

    # Shopping (15 items)
    "t-shirt", "jeans", "shoes", "dress", "jacket", "socks", "underwear", "hat", "watch", "jewelry",
    "handbag", "makeup", "skincare", "perfume", "accessories",

    # Stationery & Office Supplies (12 items)
    "notebook", "pencil", "pen", "eraser", "calculator", "stapler", "printer ink", "paper",
    "folder", "scissors", "whiteboard marker", "sticky notes",

    # Medical & Healthcare (10 items)
    "hospital", "medicine", "doctor consultation", "health checkup", "pharmacy", "vitamins",
    "gym membership", "yoga class", "therapy", "insurance premium",

    # Entertainment (10 items)
    "movie ticket", "concert", "netflix", "spotify", "amazon prime", "video game",
    "book", "magazine", "theme park", "sports event",

    # Housing & Rent (10 items)
    "rent", "mortgage", "loan payment", "insurance", "property tax", "home maintenance",
    "furniture", "painting service", "plumbing", "electrical repairs",

    # Travel & Vacation (9 items)
    "hotel booking", "flight booking", "tour package", "cruise ticket", "visa fee",
    "travel insurance", "car rental", "train pass", "resort stay",

    # Technology & Gadgets (10 items)
    "laptop", "smartphone", "tablet", "headphones", "charger", "usb cable", "external hard drive",
    "smartwatch", "gaming console", "software subscription",

    # Education (9 items)
    "school fees", "college tuition", "online course", "textbook", "educational workshop",
    "tutoring", "exam fee", "research paper", "conference registration",

    # Personal Care (10 items)
    "haircut", "spa treatment", "manicure", "pedicure", "beauty salon", "hair color",
    "massage therapy", "fragrance", "dental care", "sunscreen",

    # Donations & Charity (6 items)
    "ngo donation", "church donation", "fundraiser", "crowdfunding", "volunteering expense",
    "animal shelter donation",

    # Miscellaneous (6 items)
    "lottery ticket", "betting", "parking fee", "atm withdrawal fee", "bank service charge",
    "membership fee"
]

# Ensure categories list has the same number of elements as expenses
categories = (
    ["Groceries"] * 15 +
    ["Utilities"] * 9 +
    ["Transportation"] * 10 +
    ["Food & Dining"] * 14 +
    ["Shopping"] * 15 +
    ["Stationery & Office Supplies"] * 12 +
    ["Medical & Healthcare"] * 10 +
    ["Entertainment"] * 10 +
    ["Housing & Rent"] * 10 +
    ["Travel & Vacation"] * 9 +
    ["Technology & Gadgets"] * 10 +
    ["Education"] * 9 +
    ["Personal Care"] * 10 +
    ["Donations & Charity"] * 6 +
    ["Miscellaneous"] * 6
)

# Ensure both lists have the same length
assert len(expenses) == len(categories), f"Mismatch: {len(expenses)} expenses vs {len(categories)} categories"

# Train the model with better text preprocessing
vectorizer = CountVectorizer(analyzer='word', stop_words=None, lowercase=True)
X = vectorizer.fit_transform(expenses)
model = LogisticRegression(max_iter=200)
model.fit(X, categories)

# Save the improved model and vectorizer
joblib.dump(model, 'expense_category_model.pkl')
joblib.dump(vectorizer, 'expense_category_vectorizer.pkl')

print("✅ Improved model trained and saved successfully!")
