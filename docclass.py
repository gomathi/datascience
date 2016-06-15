import re
import math
from collections import Counter


def getwords(doc):
    splitter = re.compile('\\W*')
    # Split the words by non-alpha characters
    words = [s.lower() for s in splitter.split(doc)
             if len(s) > 2 and len(s) < 20]
    # Return the unique set of words only
    return dict([(w, 1) for w in words])


class Classifier(object):
    """docstring for Classifier"""

    def __init__(self, getfeatures=getwords):
        self.getfeatures = getfeatures
        self.categories_map = {}
        self.features_map = {}
        self.getfeatures = getfeatures

    def incr_feature_category_count(self, feature, category):
        self.features_map.setdefault(feature, {})
        self.features_map.get(feature).setdefault(category, 0)
        self.features_map[feature][category] += 1

    def incr_category_count(self, category):
        self.categories_map.setdefault(category, 0)
        self.categories_map[category] += 1

    def get_feature_category_count(self, feature, category):
        self.features_map.setdefault(feature, {})
        self.features_map.get(feature).setdefault(category, 0)
        return self.features_map[feature][category]

    def get_category_count(self, category):
        self.categories_map.setdefault(category, 0)
        return self.categories_map[category]

    def calc_category_probability(self, category):
        if category not in self.categories_map.keys():
            return 0
        if len(self.categories_map) == 0:
            return 0
        return self.categories_map[category] / sum(self.categories_map.values())

    def calc_prob_feature_given_category(self, feature, category):
        if category not in self.categories_map:
            return 0
        return self.get_feature_category_count(feature, category) / self.get_category_count(category)

    def train(self, doc, category):
        features = self.getfeatures(doc)
        for feature in features:
            self.incr_feature_category_count(feature, category)

        self.incr_category_count(category)

    def calc_weighted_probability(self, feature, category, prf, weight=1.0, assumed_probability=0.5):
        probability = prf(feature, category)

        total_count = sum([self.get_feature_category_count(feature, cat)
                           for cat in self.categories_map.keys()])

        return (probability * total_count + assumed_probability * weight) / (total_count + weight)


def sampletrain(cl):
    cl.train('Nobody owns the water.', 'good')
    cl.train('the quick rabbit jumps fences', 'good')
    cl.train('buy pharmaceuticals now', 'bad')
    cl.train('make quick money at the online casino', 'bad')
    cl.train('the quick brown fox jumps', 'good')


class NaiveBayes(Classifier):
    """docstring for NaiveBayes"""

    def __init__(self, getfeatures):
        super(NaiveBayes, self).__init__(getfeatures)
        self.thresholds = {}

    def get_threshold(self, category):
        self.thresholds.setdefault(category, 1.0)
        return self.thresholds[category]

    def set_threshold(self, category, threshold):
        self.thresholds[category] = threshold

    def calc_doc_prob(self, doc, category):
        features = self.getfeatures(doc)

        result = 1
        for feature in features:
            result *= self.calc_weighted_probability(
                feature, category, self.calc_prob_feature_given_category)
        return result

    def find_category_for_doc(self, doc):
        category_and_probability = Counter()

        for category in self.categories_map:
            category_and_probability[category] = self.calc_doc_prob(
                doc, category) * self.calc_category_probability(category)

        return category_and_probability

    def find_best_category_for_doc(self, doc, default='unknown'):
        category_and_probability = self.find_category_for_doc(doc)
        if not category_and_probability:
            return default
        best_cat, best_cat_prob = category_and_probability.most_common(1)[0]
        best_cat_threshold = self.get_threshold(best_cat)

        for cat, probability in category_and_probability.items():
            if cat == best_cat:
                continue
            if probability * best_cat_threshold > best_cat_prob:
                return default

        return best_cat
