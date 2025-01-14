# -*- coding: utf-8 -*-
"""Final2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dpWM0CkzWrYDhM7Yh3bKzm_b7yzR6uLK

# Phase 2
"""

from google.colab import drive
drive.mount('/content/drive')

import cv2
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import matplotlib.pyplot as plt

import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import cv2
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler
import os

def load_dataset():
  image_pickle_file_path = '/content/drive/MyDrive/Phase1/images.pkl'
  label_pickle_file_path = '/content/drive/MyDrive/Phase1/label.pkl'

  with open(image_pickle_file_path, 'rb') as file:
    images = pickle.load(file)

  with open(label_pickle_file_path, 'rb') as file:
    labels = pickle.load(file)


  return images, labels

# Classify the datapoints with the Random Forest Classifier
def classify(features, labels):


    test_size = 0.2
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=test_size, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)

    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy * 100:.2f}%")
    return y_test,y_pred,X_test,accuracy


images, labels = load_dataset()

"""test hsv..."""

rand_image = images[265]
rand_hsv_image = cv2.cvtColor(rand_image, cv2.COLOR_BGR2HSV)
#display image and its conversion to hsv
fig, axes = plt.subplots(1, 2, figsize=(10, 5))

# Display the first image
axes[0].imshow(rand_image)
axes[0].set_title('Original Image')

# Display the second image
axes[1].imshow(rand_hsv_image)
axes[1].set_title('HSV Image')

plt.show()

"""# Part I: Finding Important Regions

"""

import numpy as np
from sklearn.cluster import KMeans

def extract_features(image):

    def calculate_distance_from_center(image):
        height, width, _ = image.shape
        image_center = np.array([height / 2, width / 2])
        nonzero_pixels = np.transpose(np.nonzero(image[:, :, 2]))
        mean_position = np.mean(nonzero_pixels, axis=0)
        distance_from_center = np.linalg.norm(image_center - mean_position)a
        return distance_from_center

    def mean_of_distance(clusters, k):
        avg_dis_cluster = np.zeros(k)
        for index, cluster in enumerate(clusters):
            cluster_array = np.array(cluster)
            mean = np.mean(cluster_array, axis=0)
            avg_dis_cluster[index] = np.sum(np.abs(cluster_array[:, -2:] - mean[-2:]), axis=1).mean()
        avg_distance = np.sum(np.abs(np.subtract.outer(avg_dis_cluster, avg_dis_cluster))) / (
            avg_dis_cluster.shape[0] * (avg_dis_cluster.shape[0] - 1))
        return avg_distance.item()

    def mean_of_color(clusters, k):
        avg_hsv_cluster = np.zeros(k)
        for index, cluster in enumerate(clusters):
            cluster_array = np.array(cluster)
            mean = np.mean(cluster_array, axis=0)
            avg_hsv_cluster[index] = np.sum(np.abs(cluster_array[:, :3] - mean[:3]), axis=1).mean()
        avg_distance = np.sum(np.abs(np.subtract.outer(avg_hsv_cluster, avg_hsv_cluster))) / (
            avg_hsv_cluster.shape[0] * (avg_hsv_cluster.shape[0] - 1))
        return avg_distance.item()

    def size_of_clusters(clusters):
        size_of_cluster = np.array([len(i) for i in clusters])
        avg_distance = np.sum(np.abs(np.subtract.outer(size_of_cluster, size_of_cluster))) / (
            size_of_cluster.shape[0] * (size_of_cluster.shape[0] - 1))
        return avg_distance.item()

    def var_of_clusters(clusters, k):
        total_var = 0
        for i in range(k):
            cluster_colors = np.array(clusters[i])
            cluster_variance = np.var(cluster_colors)
            total_var += cluster_variance
        return total_var / k

    def mean_of_clusters(clusters, k):
        cluster_means = []
        for i in range(k):
            cluster_colors = np.array(clusters[i])
            cluster_mean = np.mean(cluster_colors, axis=0)
            cluster_means.append(cluster_mean)
        return np.mean(np.array(cluster_means))

    def variance_of_hue(clusters, k):
        hue_variances = np.zeros(k)
        for i in range(k):
            cluster_hues = np.array([pixel[0] for pixel in clusters[i]])
            hue_variance = np.var(cluster_hues)
            hue_variances[i] = hue_variance
        return np.mean(hue_variances)

    # Calculate features
    k = 5
    reshaped_image = image.reshape(-1, image.shape[-1])
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(reshaped_image)

    cluster_labels = kmeans.labels_
    clusters = [[] for _ in range(k)]
    for pixel, label in zip(reshaped_image, cluster_labels):
        clusters[label].append(pixel)

    features = {}
    features['mean_distance'] = mean_of_distance(clusters, k)
    features['mean_color'] = mean_of_color(clusters, k)
    features['size_difference'] = size_of_clusters(clusters)
    features['variances'] = var_of_clusters(clusters, k)
    features['means'] = mean_of_clusters(clusters, k)
    features['variance_of_hue'] = variance_of_hue(clusters, k)
    features['distance_from_center'] = calculate_distance_from_center(image)

    features_array = np.array(list(features.values()))

    return features_array

# Assuming you have an image stored as a numpy array
rand_image = np.random.rand(100, 100, 3) * 255  # Example random image
features = extract_features(rand_image)

print(features)

"""Extract features"""

first_100_images = images[:100]

# Convert images to HSV format
hsv_images = [cv2.cvtColor(image, cv2.COLOR_BGR2HSV) for image in first_100_images]

# Extract features from the selected images
features_list = [extract_features(image) for image in hsv_images]


# Convert the list of features into a 2D numpy array
X_train = np.array(features_list)

# Extract labels for the first 100 images
y_train = np.array(labels[:100])

# Check the shapes of X_train and y_train
print(X_train.shape)  # This will output the shape of the feature array
print(y_train.shape)  # This will output the shape of the label array

print("Number of dimensions:", X_train.ndim)

print(features.shape)

def calculate_correlation(features1, features2):
    correlation = np.corrcoef(features1, features2)[0, 1]
    return correlation

def calculate_f1_score(accuracy, correlation):
    precision = accuracy
    recall = correlation
    f1_score = 2 * (precision * recall) / (precision + recall)
    return f1_score


# Initialize an empty list to store average features for each cluster of each image
average_cluster_features_per_image = []

# Iterate over the feature vectors in X_train
for features in X_train:
    # Reshape the features array to 2D if it's 1D
    if len(features.shape) == 1:
        features = features.reshape(-1, 1)

    # Apply KMeans clustering
    num_clusters = 3
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(features)
    cluster_labels = kmeans.labels_
    cluster_centers = kmeans.cluster_centers_

    # List to store average features for each cluster in this image
    average_features_per_cluster = []

    # Iterate over each cluster to calculate average features
    for i in range(num_clusters):
        # Filter the features that belong to the current cluster
        cluster_features = features[cluster_labels == i]

        # Calculate the average of features in this cluster
        avg_cluster_features = np.mean(cluster_features, axis=0)

        average_features_per_cluster.append(avg_cluster_features)

    # Append the average features of clusters for this image to the main list
    average_cluster_features_per_image.append(average_features_per_cluster)

# Now, average_cluster_features_per_image contains the average features for each cluster of each image.

print(type(labels))

print(X_train)

import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

def classify(features, labels):
    test_size = 0.2
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=test_size, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy * 100:.2f}%")
    return y_test, y_pred, X_test, accuracy

def cluster_image(image, num_clusters=5):
    reshaped_image = image.reshape(-1, image.shape[-1])
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(reshaped_image)
    cluster_labels = kmeans.labels_
    clusters = [reshaped_image[cluster_labels == i] for i in range(num_clusters)]
    return cluster_labels, clusters

def rank_clusters_based_on_impact(clusters, features, labels):
    scores = []
    for cluster_idx, cluster in enumerate(clusters):
        cluster_indices = np.where(labels == cluster_idx)[0]

        # Check if the cluster is not empty
        if len(cluster_indices) > 0:
            modified_features = np.delete(features, cluster_indices, axis=0)
            modified_labels = np.delete(labels, cluster_indices, axis=0)

            # Train and evaluate the classifier on the modified dataset
            _, _, _, accuracy = classify(modified_features, modified_labels)

            scores.append((cluster_idx, accuracy))

    # Rank clusters based on their effect on accuracy
    scores.sort(key=lambda x: x[1])  # Sort by accuracy in ascending order

    return scores if scores else [(None, 0)]  # Return a default value if scores is empty

def clusters_to_image(cluster_labels, shape, clusters):
    clustered_image = np.zeros(shape + (3,), dtype=np.uint8)
    for i, cluster in enumerate(clusters):
        mask = cluster_labels == i
        mask = mask.reshape(shape)  # Reshape the mask to match the image shape
        clustered_image[mask] = np.mean(cluster, axis=0)
    return clustered_image

def flatten_images(images):
    return np.array([image.flatten() for image in images])

flattened_images = flatten_images(first_100_images)

NUM_CLUSTERS = 3
prev_accuracy = None

# Set initial value for NUM_ITERATIONS
NUM_ITERATIONS = 5

for iteration in range(NUM_ITERATIONS):
    for image, label in zip(first_100_images, y_train):  # Use y_train consistently
        cluster_labels, clusters = cluster_image(image, num_clusters=NUM_CLUSTERS)

        # Convert cluster_labels back to the original image shape for visualization
        clustered_image = clusters_to_image(cluster_labels, image.shape[:-1], clusters)

        # Rank clusters based on their impact on the model
        ranked_clusters = rank_clusters_based_on_impact(clusters, flattened_images, y_train)

        # Check if ranked_clusters is not empty
        if ranked_clusters:
            least_impactful_cluster_index = ranked_clusters[-1][0]
            mask = cluster_labels == least_impactful_cluster_index
            mask = mask.reshape(image.shape[:-1])
            # Remove cluster indices from the flattened images
            flattened_images = flattened_images[~mask.flatten()]

        # Display the original image and the clustered image side by side
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        axes[0].imshow(image)
        axes[0].set_title('Original Image')
        axes[0].axis('off')

        axes[1].imshow(clustered_image)
        axes[1].set_title('Clustered Image')
        axes[1].axis('off')

        plt.show()

    # Evaluate the model on the entire modified dataset after each iteration
    _, _, _, accuracy = classify(flattened_images, y_train)
    print(f"Iteration {iteration + 1}: Accuracy: {accuracy * 100:.2f}%")

    # Print the cluster rankings for the current iteration
    for cluster, rank in ranked_clusters:
        print(f"Iteration {iteration + 1} - Cluster: {cluster} - Rank: {rank:.4f}")

    # Print a separator for better readability
    print("="*50)

    # Update the previous accuracy for the next iteration comparison
    prev_accuracy = accuracy

print("End of iterations.")

def flatten_images(images):
    flattened = np.array([image.flatten() for image in images])
    print(f"Shape of flattened images: {flattened.shape}")  # Debug print
    return flattened
flatten_images(first_100_images)

"""# Part II: Clustering

"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
import numpy as np
import pickle

# Your existing functions like load_dataset(), extract_features(), etc.

def classify(features, labels):
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    # Initialize and train classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Predict
    y_pred = clf.predict(X_test)

    # Calculate accuracy and return
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy

def select_important_features(X, y):
    # Train a random forest classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)

    # Predict probabilities and get the confidence for each class
    y_probs = clf.predict_proba(X)
    confidences = np.max(y_probs, axis=1)

    # Identify the 20% of data with the lowest confidence
    threshold = np.percentile(confidences, 20)
    least_confident_indices = np.where(confidences < threshold)[0]

    # Start feature selection
    selected_features = []
    best_f1 = 0

    while True:
        for feature in range(X.shape[1]):
            if feature not in selected_features:
                current_features = np.delete(X, selected_features + [feature], axis=1)

                current_accuracy = classify(current_features, y)
                if current_accuracy > best_f1:
                    best_f1 = current_accuracy
                    selected_features.append(feature)
                    break

        if len(selected_features) == X.shape[1]:
            break

    return selected_features, best_f1

# Assuming you have loaded images and labels and processed them as X_train and y_train respectively
selected_features, best_f1 = select_important_features(X_train, y_train)
print(f"Selected features: {selected_features}")
print(f"Best f1-score: {best_f1}")

# Now you can train your final classifier using only the selected features (X_train[:, selected_features])
# And evaluate its performance as needed.