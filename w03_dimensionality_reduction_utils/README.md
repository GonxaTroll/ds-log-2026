# Week 03 - Dimensionality reduction techniques

## Context and Overview

TL;DR: I’ve created [a repository](https://github.com/GonxaTroll/dimensionality-reduction) featuring methods to analyze and interpret the outputs of a Principal Component Analysis (PCA) model. My plan is to continue refining this and eventually expand it to include other models.

I have frequently used dimensionality reduction techniques—primarily PCA—throughout my past work.

I believe it is crucial to build PCA models with rigor. I often see cases where PCA is used strictly as a "black box" compressor to feed data into another machine learning model, without much regard for the quality of that compression. Like any other model, the residuals must be analyzed; the model may fail to fit certain data points (outliers) or be heavily skewed by extreme individuals. Furthermore, when used for exploratory analysis, PCA results must be properly validated.

Beyond simple compression, PCA is an incredibly powerful tool for discovering hidden patterns in data.

I originally wrote this code quite a while ago to extract deeper insights from my models. While other repositories exist, I found they often lacked specific calculations necessary for a truly intuitive understanding. This week, I focused on reformatting and improving the code for better reusability in future projects.

## Topics Covered
- Unsupervised learning
- Dimensionality reduction techniques
- Principal Component Analysis.

## Notes

