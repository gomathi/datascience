import matplotlib.pyplot as plt
import numpy as np
import random
import math
import scipy
from scipy import stats

# Creating card array to store 1(indicating Ace) to 10 for 4 different
# types, and 10 value for King, Jack and Queen

cards = [i for category in range(4) for i in range(1, 11)]
cards.extend([10 for category in range(4) for i in range(3)])

# Plotting relative frequency chart for the cards in our hands

plt.bar(np.arange(len(set(cards))), scipy.stats.relfreq(cards, numbins=10).frequency, 1.0,
        color='blue')
plt.title("Histogram of cards distribution")
plt.xlabel("Card value")
plt.ylabel("Frequency")

plt.show()

print("Mean of population :", np.mean(cards))
print("Mode of the population :", stats.mode(cards).mode[0])
print("Median of the population :", np.median(cards))
print("Variance of the population :", np.var(cards))
print("Standard deviation of population:", np.std(cards))

# Building sample means, and plotting the histogram

sampled_means = []
sample_size = 3
means_size = 250

random.shuffle(cards)

for _ in range(means_size):
    sample = []
    for _ in range(sample_size):
        sample.append(cards[random.randint(0, len(cards) - 1)])
    sampled_means.append(sum(sample))


plt.bar(np.array(sorted(set(sampled_means))), scipy.stats.relfreq(sampled_means, numbins=len(set(sampled_means))).frequency, 1.0,
        color='blue')
plt.title("Histogram of sampling distribution")
plt.xlabel("Sample mean")
plt.ylabel("Frequency")

plt.show()

print("Mean of sampling distribution :", np.mean(sampled_means))
print("Mode of sampling distribution :", stats.mode(sampled_means).mode[0])
print("Median of the sampling distribution :",
      np.median(sampled_means))
print("Variance of the sampling distribution :", np.var(sampled_means))
print("Standard deviation of sampling distribution:", np.std(sampled_means))
print("Standard deviation of sampling distribution - using the formula:",
      np.std(cards) / math.sqrt(sample_size))
