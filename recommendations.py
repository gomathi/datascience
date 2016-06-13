import similarity
from collections import Counter

critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 'The Night Listener': 3.0}, 'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 3.5}, 'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0, 'Superman Returns': 3.5, 'The Night Listener': 4.0}, 'Claudia Puig': {'Snakes on a Plane': 3.5,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           'Just My Luck': 3.0, 'The Night Listener': 4.5, 'Superman Returns': 4.0, 'You, Me and Dupree': 2.5}, 'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 2.0}, 'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5}, 'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


def invert_input(input):
    result = {}
    for candidate, pref_list in input.items():
        for item, score in pref_list.items():
            result.setdefault(item, {})
            result[item][candidate] = score

    return result


def recommend_similar_candidates(icandidate, prefs, sim_calculator=similarity.calc_euclidean_distance, count=5):
    ritems = Counter()
    for candidate, pref_list in prefs.items():
        if candidate != icandidate:
            fkeys = prefs[icandidate].keys()
            skeys = prefs[candidate].keys()
            common_keys = list(fkeys & skeys)
            fscores = [prefs[icandidate][ck] for ck in common_keys]
            sscores = [prefs[candidate][ck] for ck in common_keys]
            ritems[candidate] = sim_calculator(fscores, sscores)

    return ritems.most_common(count)


def recommend_items(icandidate, prefs, sim_calculator=similarity.calc_euclidean_distance, count=5):
    similarity_scores = {candidate: sim_score for candidate, sim_score in recommend_similar_candidates(
        icandidate, prefs, sim_calculator, len(prefs))}
    candidate_items = set([item for pref_list in prefs.values(
    ) for item in pref_list.keys() if item not in prefs[icandidate]])

    ritems = Counter()

    for candidate_item in candidate_items:
        sim_score_weighted_score_list = [(similarity_scores[candidate], prefs_list[candidate_item] * similarity_scores[candidate]) for candidate,
                                         prefs_list in prefs.items() if candidate_item in prefs_list and candidate in similarity_scores]
        sim_scores_sum = sum([sim_score for sim_score,
                              _ in sim_score_weighted_score_list])
        weighted_scores_sum = sum(
            [weighted_score for _, weighted_score in sim_score_weighted_score_list])
        ritems[candidate_item] = weighted_scores_sum / sim_scores_sum

    return ritems.most_common(count)


def cal_similar_items(prefs, n=10, sim_calculator=similarity.calc_euclidean_distance):
    inverted_input = invert_input(prefs)

    result = {}

    for item in inverted_input:
        similar_items = recommend_similar_candidates(
            item, inverted_input, sim_calculator, n)
        result[item] = similar_items

    return result


def calc_all_sim_items(item_prefs, sim_calculator=similarity.calc_euclidean_distance, count=20):
    result = {}
    for item in item_prefs:
        sim_items = recommend_similar_candidates(
            item, item_prefs, sim_calculator, count)
        result[item] = {sim_item: sim_score for sim_item,
                        sim_score in sim_items}
    return result


def getRecommendedItemsForGivenCandidate(candidate_and_item_score, sim_items, n=5):
    result = Counter()
    unrated_items = sim_items.keys() - candidate_and_item_score.keys()
    rated_items = sim_items.keys() & candidate_and_item_score.keys()
    for unrated_item in unrated_items:
        common_items = list(sim_items[unrated_item].keys() & rated_items)
        sim_items_scores = [sim_items[unrated_item][common_item]
                            for common_item in common_items]
        candidate_ratings = [candidate_and_item_score[
            common_item] for common_item in common_items]
        normalized_score = sum([(sim_items_score * candidate_rating) for sim_items_score,
                                candidate_rating in zip(sim_items_scores, candidate_ratings)]) / sum(sim_items_scores)
        result[unrated_item] = normalized_score

    return result.most_common(n)
