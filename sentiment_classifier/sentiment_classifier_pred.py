import json
import os
import pickle
import re
import numpy as np

REPLACE_NO_SPACE = re.compile("[.;:!\'?,\"()\[\]]")
REPLACE_WITH_SPACE = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)")


def preprocess(reviews):
    reviews = [REPLACE_NO_SPACE.sub("", line.lower()) for line in reviews]
    reviews = [REPLACE_WITH_SPACE.sub(" ", line) for line in reviews]
    reviews = [line.encode('ascii', 'ignore').decode("utf-8") for line in reviews]
    return reviews


def get_youtube_comments(json_path):
    with open(json_path, 'r') as j:
        json_data = json.load(j)
        # comments = json_data["comments"]
        return json_data


class SentimentPred:
    def __init__(self, model_path, cv_path):
        # load the model from disk
        self.model = None
        try:
            self.model = pickle.load(open(model_path, 'rb'))
        except Exception as e:
            print(e)
            print("Failed loading pickled model ...")

        self.cv = None
        try:
            self.cv = pickle.load(open(cv_path, 'rb'))
        except Exception as e:
            print(e)
            print("Failed loading cv ... ")

    def vectorize(self, data_clean):
        return self.cv.transform(data_clean)

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


if __name__ == '__main__':
    model_path = "./imdb_lg_classifier_09132020.pkl"
    cv_path = "./count_vectorizer_09132020.pkl"

    classifier = SentimentPred(model_path, cv_path)

    json_dir_from = "../data_sentiment_score/data"
    json_dir_to = "../data_sentiment_score/sentiment_score"

    # video_json_files = ["04U3DTGHcXg.json"]
    video_json_files = ["5eGpvi_RgBk.json"]

    if not os.path.isdir(json_dir_to):
        os.mkdir(json_dir_to)

    for video in video_json_files:
        json_data = get_youtube_comments(os.path.join(json_dir_from, video))
        comments = json_data["comments"]
        comments_clean = preprocess(comments)
        comments_clean_vec = classifier.vectorize(comments_clean)

        pred_prob = classifier.predict_prob(comments_clean_vec) # ndarray, dimension: n of examples X 2
        # print(f"type: {type(pred_prob)}, shape: {pred_prob.shape}")
        pred = classifier.predict(comments_clean_vec)

        comment_count = len(comments)
        print(f"comment count: {comment_count}")
        json_data["comment_count"] = comment_count

        comment_score = np.sum(pred_prob, axis=0)[1]/comment_count
        print(f"comment score: {comment_score}")
        json_data["comment_score"] = comment_score

        new_file_path = os.path.join(json_dir_to, video[:-5] + "_comment.json")
        with open(new_file_path, 'w') as f:
            json.dump(json_data, f, indent=4)

        for idx in range(len(comments)):
            print("\n=====================")
            print(f"example: {comments[idx]}")
            print(f"example clean: {comments_clean[idx]}")
            print(f"pred_prob: {pred_prob[idx]}")
            print(f"pred: {pred[idx]}")

            # result = loaded_model.score(X_test, Y_test)
