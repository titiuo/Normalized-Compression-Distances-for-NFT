# Implementation of compression distance to predict the price of NFTs

## Abstract
Given a collection of NFTs listed on a marketplace, the goal is to develop an algorithm capable of predicting the price of any NFT in the collection based on the prices of others and their compression distances relative to the target NFT.

## Problem
How can we predict the price of an NFT within a given collection with minimal relative error?

## Method
To compute the compression distance, we first used the Normalized Compression Distance (NCD) to evaluate visual similarities between two NFTs using data compression.

We also explored a second approach using the Normalized Information Distance (NID) by leveraging Kolmogorov complexity and the frequency of NFT attributes, i.e., the probability of attribute appearances.

After computing distances between NFTs, several prediction methods were tested:
- **Closest match:** Assign the price of the nearest NFT in the collection.
- **Top x matches:** Assign the minimum price from the x nearest NFTs.
- **Average pricing:** Calculate an average price weighted by distances.
- **Weighted function approach:** Use a function to adjust the weight of closer versus farther NFTs.
- **Neural network:** Use a neural network that takes prices and distances of all NFTs in the collection to predict the target price.

## Results
The first approach (NCD) yielded good results but was time-intensive (1 second per comparison, approximately 10 minutes for a thousand NFTs). Additionally, inconsistencies in compression (Z(x,x) ≠ Z(x) using the `lzma` library) posed challenges.

The second approach (NID) was faster (under 1 minute for an entire collection) and more consistent for computing distances.

Price prediction results with and without a price filter (≤ 11 Sol, covering 95.2% of listed NFTs):
- **Closest match:**
  - Δmean = 3.2 Sol (61.2% relative error, due to inflated offers).
  - Filtered (≤ 11 Sol): Δmean = 2.1 Sol (50.5% relative error).
- **Top x matches (x=3):**
  - Δmean = 2.7 Sol (51.8% relative error, minimum price approach underestimates values).
  - Filtered (≤ 11 Sol): Δmean = 1.26 Sol (30.3% relative error).
- **Average price:**
  - Δmean = 2.66 Sol (50.9% relative error).
  - Filtered (≤ 11 Sol): Δmean = 1.71 Sol (41.2% relative error).
- **Weighted function approach:**
  - Δmean = 2.64 Sol (50.4% relative error).
  - Filtered (≤ 11 Sol): Δmean = 1.7 Sol (40.9% relative error).
- **Neural network approach:**
  - Δmean = 2.2-2.6 Sol (57.8% relative error, requires more consistent data).
  - Filtered (≤ 11 Sol): Δmean = 1.39 Sol (33.7% relative error).

## Discussion
Results were obtained using a single collection of 280 NFTs, highlighting the potential issue of insufficient data. However, our code can be applied to multiple collections for further analysis and validation.

## Bibliography
- GitHub for NCD: [https://github.com/alephmelo/pyncd](https://github.com/alephmelo/pyncd)
- Explanation of NCD for images: [https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7512663/](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7512663/)
- Magic Eden API: [https://docs.magiceden.io/reference/solana-overview](https://docs.magiceden.io/reference/solana-overview)
- Sandbar NFT collection: [https://magiceden.io/marketplace/sandbar](https://magiceden.io/marketplace/sandbar)

