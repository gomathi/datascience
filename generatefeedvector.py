import feedparser
import re
import similarity
from collections import deque
from neo4jrestclient.client import GraphDatabase
import random


def getwordcounts(url):
    d = feedparser.parse(url)
    wc = {}
    # Loop over all the entries
    for e in d.entries:
        if 'summary' in e:
            summary = e.summary
        else:
            summary = e.description
        # Extract a list of words
        words = getwords(e.title + ' ' + summary)
        for word in words:
            wc.setdefault(word, 0)
            wc[word] += 1
    return d.feed.title, wc


def getwords(html):
        # Remove all the HTML tags
    txt = re.compile(r'<[^>]+>').sub('', html)
    # Split words by all non-alpha characters
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    # Convert to lowercase
    return [word.lower() for word in words if word != '']


def parse_files(fileslist):
    apcount = {}
    wordcounts = {}
    for feedurl in open(fileslist):
        try:
            title, wc = getwordcounts(feedurl)
            wordcounts[title] = wc
            for word, count in wc.items():
                apcount.setdefault(word, 0)
                if count > 1:
                    apcount[word] += 1
        except:
            pass
    return apcount, wordcounts


def filter_less_common_words(apcount, tot_files):
    less_common_words = []
    for word, count in apcount.items():
        occurrence_percentage = count / tot_files
        if occurrence_percentage > 0.1 and occurrence_percentage < 0.5:
            less_common_words.append(word)

    return less_common_words


def get_blog_matrix(fileslist):
    apcount, wordcounts = parse_files(fileslist)
    less_common_words = filter_less_common_words(apcount, len(wordcounts))
    column_names = [
        less_common_word for less_common_word in less_common_words]
    blog_matrix = {}
    for blog_name, words in wordcounts.items():
        blog_matrix.setdefault(blog_name, {})
        for less_common_word in less_common_words:
            blog_matrix[blog_name][less_common_word] = words[
                less_common_word] if less_common_word in words else 0
    return column_names, blog_matrix


def print_blog_matrix(fileslist, out_file):
    column_names, blog_matrix = get_blog_matrix(fileslist)
    out = open(out_file, 'w')
    out.write("blog-name")
    for column_name in column_names:
        out.write("\t" + column_name)
    out.write("\n")

    for blog_name, words in blog_matrix.items():
        out.write(blog_name)
        for column_name in column_names:
            out.write("\t%d" % words[column_name])
        out.write("\n")


def read_blog_matrix(input_file):
    rows = []
    columns = []
    data = []

    with open(input_file, 'r') as f:
        columns = [word for word in
                   f.readline().split("\t")[1:]]
        for index, line in enumerate(f):
            row = line.split("\t")
            rows.append(row[0])
            data.append([float(val.strip()) for val in row[1:]])

    return rows, columns, data


class BiCluster(object):
    """docstring for BiCluster"""

    def __init__(self, vec, ide, left=None, right=None, distance=0.0, is_branch=False):
        self.vec = vec
        self.ide = ide
        self.left = left
        self.right = right
        self.distance = distance
        self.is_branch = is_branch

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "left={},right={},is_branch={}".format(self.left.ide, self.right.ide, self.is_branch)

    def __eq__(self, other):
        return self.ide == other.ide

    def __hash__(self):
        return hash(self.ide)


def modified_pearson(first, second):
    return 1 - similarity.calc_pearson_coefficient(first, second)


def cluster_blogs(rows, data, distance_calc=modified_pearson):
    cached_dist_map = {}
    clusters = [BiCluster(data[i], ide=i) for i in range(len(data))]

    branch_id = 0

    while len(clusters) > 1:
        lowest_dist = distance_calc(clusters[0].vec, clusters[1].vec)
        lowest_pairs = (0, 1)

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                if not (i, j) in cached_dist_map:
                    dist = distance_calc(clusters[i].vec, clusters[1].vec)
                    cached_dist_map[(i, j)] = dist
                else:
                    dist = cached_dist_map[(i, j)]

                if dist < lowest_dist:
                    lowest_dist = dist
                    lowest_pairs = (i, j)

        left, right = lowest_pairs
        new_cluster_vec = [(clusters[left].vec[i] + clusters[right].vec[i]
                            ) / 2.0 for i in range(len(data[0]))]
        new_cluster = BiCluster(new_cluster_vec, "br" + str(branch_id), left=clusters[left],
                                right=clusters[right], distance=lowest_dist, is_branch=True)
        branch_id += 1
        del clusters[right]
        del clusters[left]
        del cached_dist_map[lowest_pairs]
        clusters.append(new_cluster)

    return clusters[0]


def create_gnode(gdb, bivector_node):
    bivector_gnode = gdb.nodes.create(
        ide=bivector_node.ide, vec=bivector_node.vec)
    return bivector_gnode


def create_neo4j_graph(bicluster_root):
    gdb = GraphDatabase("http://localhost:7474/",
                        username="neo4j", password="neo4j12")

    traverse_queue = deque([bicluster_root])
    cnode_and_gnode = {}

    while len(traverse_queue) > 0:
        curr = traverse_queue.popleft()
        for node in (curr, curr.left, curr.right):
            if node and node not in cnode_and_gnode:
                gnode = create_gnode(gdb, node)
                cnode_and_gnode[node] = gnode
        curr_gnode = cnode_and_gnode[curr]
        if curr.left:
            traverse_queue.append(curr.left)
            curr_gnode.relationships.create(
                "Left", cnode_and_gnode[curr.left], distance=curr.distance)
        if curr.right:
            traverse_queue.append(curr.right)
            curr_gnode.relationships.create(
                "Right", cnode_and_gnode[curr.right], distance=curr.distance)


def print_tree_cluster(root, rows):
    if not root.is_branch:
        print(rows[root.ide])
        return [rows[root.ide]]

    left = print_tree_cluster(root.left, rows)
    right = print_tree_cluster(root.right, rows)

    result = left + right
    print(result)
    return result


def generate_random_clusters(data, k):
    min_gap_pairs = [(min(column), max(column) - min(column))
                     for column in zip(*data)]
    clusters = [[random.random() * min_gap_pairs[j][1] + min_gap_pairs[j][0]
                 for j in range(len(data[0]))] for _ in range(k)]
    return clusters


def kcluster(rows, data, k, distance_calculator=modified_pearson):
    clusters = generate_random_clusters(data, k)
    last_matches = None
    new_clusters_data = None

    for iteration in range(100):
        best_matches = [[] for i in range(k)]

        for rowid in range(len(data)):
            row = data[rowid]
            best_match = 0
            for clusterid in range(k):
                d = distance_calculator(clusters[clusterid], row)
                if d < distance_calculator(clusters[best_match], row):
                    best_match = clusterid
            best_matches[best_match].append(rowid)

        if best_matches == last_matches:
            break
        last_matches = best_matches

        new_clusters_data = [[data[rowid] for rowid in last_match]
                             for last_match in last_matches]
        new_clusters = [[sum(row) / len(row) for row in zip(*cluster)]
                        for cluster in new_clusters_data]
        clusters = new_clusters

    blog_clusters = [[rows[blogid] for blogid in cluster]
                     for cluster in last_matches]
    return blog_clusters, clusters, new_clusters_data


def kcluster_and_print_totaldistance(rows, data, k, distance_calculator=modified_pearson):
    blog_clusters, clusters, new_clusters_data = kcluster(
        rows, data, k, distance_calculator)
    total_distance_list = []
    for index, clustered_list in enumerate(new_clusters_data):
        clustered_list_copy = [clusters[index]]
        clustered_list_copy.extend(clustered_list)
        total_distance = sum([distance_calculator(first, second)
                              for first in clustered_list_copy for second in clustered_list_copy if first != second])
        total_distance_list.append(total_distance)

    return blog_clusters, clusters, total_distance_list


rows, columns, data = read_blog_matrix(
    "/workplace/projects/datascience/blog_matrix.txt")
for i in range(3, 30):
    while True:
        try:
            _, _, total_distance_list = kcluster_and_print_totaldistance(
                rows, data, i)
            print(i, total_distance_list)
            break
        except:
            pass
