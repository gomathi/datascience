import math


def calc_mean(first):
    if not first:
        return 0
    return sum(first) / len(first)


def calc_standard_deviation(input):
    if not input:
        return 0
    mean = calc_mean(input)
    differences = [xi - mean for xi in input]
    squared_differences = [difference ** 2 for difference in differences]
    std_deviation = math.sqrt(sum(squared_differences) / len(input))
    return std_deviation


def calc_covariance(first, second):
    if not first and not second:
        return 0

    if len(first) != len(second):
        raise ValueError(
            "Given length of first vector is not equivalent to length of second vector")

    fmean = calc_mean(first)
    smean = calc_mean(second)

    fdifferences = [fi - fmean for fi in first]
    sdifferences = [si - smean for si in second]
    sum_of_products = sum(
        [fi * si for fi, si in zip(fdifferences, sdifferences)])
    return sum_of_products / len(first)


def calc_euclidean_distance(first, second):
    if not first and not second:
        return 0

    if len(first) != len(second):
        raise ValueError(
            "Given length of first vector is not equivalent to length of second vector")

    differences = [fi - si for fi,
                   si in zip(first, second)]
    squared_differences = [difference ** 2 for difference in differences]
    distance = math.sqrt(sum(squared_differences))
    return 1 / (1 + distance)


def calc_pearson_coefficient(first, second):
    if not first and not second:
        return 0

    return calc_covariance(first, second) / (calc_standard_deviation(first) * calc_standard_deviation(second))
