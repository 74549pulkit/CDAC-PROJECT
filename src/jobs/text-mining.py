import pandas as pd
import json
import joblib
data1=pd.read_json(r'D:/project-1/train.json')
data2=data1['value']
# Convert string representations of dictionaries to dictionaries
data = [json.loads(d) if isinstance(d, str) else d for d in data2]

# Convert list of dictionaries to DataFrame
df = pd.DataFrame(data)


from sklearn.feature_extraction.text import TfidfVectorizer
tf=TfidfVectorizer(max_features = 1000)
X = tf.fit_transform(data['Phrase']).toarray()
X = pd.DataFrame(X,columns=tf.get_feature_names())
y = data.iloc[:, 3]
y
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y , test_size=0.3, random_state=123)

from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
# Model Generation Using Multinomial Naive Bayes
clf = MultinomialNB().fit(X_train, y_train)
predicted= clf.predict(X_test)
print("MultinomialNB Accuracy:",metrics.accuracy_score(y_test, predicted))

joblib.dump(clf, 'model1.pkl')