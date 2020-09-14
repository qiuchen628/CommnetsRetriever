import json
import os
import pickle
import re

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

REPLACE_NO_SPACE = re.compile("[.;:!\'?,\"()\[\]]")
REPLACE_WITH_SPACE = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)")

class SentimentClassifier:
    def __init__(self, data_dir):
        self.cv = CountVectorizer(binary=True)
        self.model = None
        self.c = 0.05

        ## load data
        self.reviews_train = []
        for line in open(os.path.join(data_dir, 'full_train.txt'), 'r'):
            self.reviews_train.append(line.strip())
        self.reviews_test = []
        for line in open(os.path.join(data_dir, 'full_test.txt'), 'r'):
            self.reviews_test.append(line.strip())
        self.y = [1 if i < 12500 else 0 for i in range(25000)]
        self.y_test = [1 if i < 12500 else 0 for i in range(25000)]

        ## preprocess data
        self.reviews_train_clean = self.preprocess(self.reviews_train)
        self.reviews_test_clean = self.preprocess(self.reviews_test)

        ## vectorize data
        self.X = self.vectorize(self.reviews_train_clean, is_train_set=True)
        self.X_test = self.vectorize(self.reviews_test_clean, is_train_set=False)

        ## split train val
        self.X_train, self.X_val, self.y_train, self.y_val = \
            train_test_split(self.X, self.y, train_size=0.75)

    @staticmethod
    def preprocess(reviews):
        reviews = [REPLACE_NO_SPACE.sub("", line.lower()) for line in reviews]
        reviews = [REPLACE_WITH_SPACE.sub(" ", line) for line in reviews]
        reviews = [line.encode('ascii', 'ignore').decode("utf-8") for line in reviews]
        return reviews

    def vectorize(self, data_clean, cv_dir="./", is_train_set=False):
        if is_train_set:
            self.cv.fit(self.reviews_train_clean)
            pickle.dump(self.cv, open(os.path.join(cv_dir, "count_vectorizer_09132020.pkl"), "wb"))
        return self.cv.transform(data_clean)

    def train(self):
        self.model = LogisticRegression(C=self.c)
        self.model.fit(self.X, self.y)
        print("Final Train Accuracy: {}".format(accuracy_score(self.y, self.model.predict(self.X))))
        print("Final Test Accuracy: {}".format(accuracy_score(self.y_test, self.model.predict(self.X_test))))
        # Final Accuracy: 0.88128

    def pickle_model(self, dir_path, file_name):
        if self.model is not None:
            pickle.dump(self.model, open(os.path.join(dir_path, file_name), 'wb'))

    def load_model(self, model_path):
        if os.path.isfile(model_path):
            try:
                model = pickle.load(open(model_path, 'rb'))
                print("Successfully loaded mdoel!!")
                return model
            except Exception as e:
                print(e)
                print("Failed to load the model...")
        else:
            print("No model found with this path: {}".format(model_path))

    def predict_prob(self, X):
        # X is array_like, (n_samples, n_features)
        if self.model is not None:
            return self.model.predict_proba(X)
        else:
            print("no valid model found...")
            return None

    def predict(self, X):
        if self.model is not None:
            return self.model.predict(X)
        else:
            print("no valid model found...")
            return None

def get_youtube_comments(json_path):
    comments = []
    with open(json_path, 'r') as j:
        json_data = json.load(j)
        comments = json_data["comments"]
        return comments

if __name__ == '__main__':
    base_data_dir = "/home/sams/Documents/aclImdb/movie_data"
    classifier = SentimentClassifier(base_data_dir)
    classifier.train()

    model_dir = "./"
    model_name = "imdb_lg_classifier_09132020.pkl"
    classifier.pickle_model(model_dir, model_name)

    # examples = []
    # for line in open(os.path.join(base_data_dir, 'full_train.txt'), "r"):
    #     examples.append(line.strip())
    # examples_pos = examples[:12500]
    # examples_neg = examples[12500:]

    json_dir = "../classifier_test_data"
    # video_json_files = ["04U3DTGHcXg.json"]
    video_json_files = ["5eGpvi_RgBk.json"]
    for video_comment in video_json_files:
        examples = get_youtube_comments(os.path.join(json_dir, video_comment))
        print(examples)
        examples_clean = classifier.preprocess(examples)
        print(examples_clean)
        examples_clean_vec = classifier.vectorize(examples_clean)
        # print(examples_clean_vec)

        pred_prob = classifier.predict_prob(examples_clean_vec)
        pred = classifier.predict(examples_clean_vec)

        for idx in range(len(examples)):
            print("\n=====================")
            print(f"example: {examples[idx]}")
            print(f"example clean: {examples_clean[idx]}")
            print(f"pred_prob: {pred_prob[idx]}")
            print(f"pred: {pred[idx]}")

    #
    #
    # # examples = example_train_pos + example_train_neg + example_test_pos + example_test_neg
    # examples_clean = classifier.preprocess(examples_pos)
    # examples_clean_vec = classifier.vectorize(examples_clean)
    # pred_prob = classifier.predict_prob(examples_clean_vec)
    #
    # # print("Results prob:")
    # # for p in pred_prob:
    # #     print(p)
    # #
    # # print('\n')
    #
    # pred = classifier.predict(examples_clean_vec)
    # # print("Results: ")
    # # for pp in pred:
    # #     print(pp)
    #
    print("Done")