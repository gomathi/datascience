import similarity
from collections import Counter

critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 'The Night Listener': 3.0}, 'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 3.5}, 'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0, 'Superman Returns': 3.5, 'The Night Listener': 4.0}, 'Claudia Puig': {'Snakes on a Plane': 3.5,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           'Just My Luck': 3.0, 'The Night Listener': 4.5, 'Superman Returns': 4.0, 'You, Me and Dupree': 2.5}, 'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 2.0}, 'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5}, 'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


def recommend_similar_items(item_name, prefs, sim_calculator=similarity.calc_euclidean_distance, count=5):
    ritems = Counter()
    for candidate, pref_list in prefs.items():
        if candidate != item_name:
            fkeys = prefs[item_name].keys()
            skeys = prefs[candidate].keys()
            common_keys = list(fkeys & skeys)
            fscores = [prefs[item_name][ck] for ck in common_keys]
            sscores = [prefs[candidate][ck] for ck in common_keys]
            ritems[candidate] = sim_calculator(fscores, sscores)

    return ritems.most_common(count)
