import cv2
import numpy as np
from sklearn.cluster import KMeans,DBSCAN
import matplotlib.pyplot as plt
import crewai


def make_cluster(img_path, satellite_path,cn, n_clusters=12):
    # Load the segmented image
    image = cv2.imread(img_path)
    sat_img = cv2.imread(satellite_path)
    
    # Define the color range for red in HSV
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    # Convert the image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Create masks for red and dark red
    mask_red = cv2.inRange(hsv_image, lower_red, upper_red)
    mask_dark_red = cv2.inRange(hsv_image, lower_red2, upper_red2)

    # Combine masks
    mask = cv2.bitwise_or(mask_red, mask_dark_red)

    # Find the coordinates of the land pixels (red areas)
    land_pixels = np.column_stack(np.where(mask > 0))

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(land_pixels)
    
    # Extract the coordinates of the cluster centers
    cluster_centers = kmeans.cluster_centers_

    print(f'Estimated number of clusters: {n_clusters}')
    NP=[]
    for cluster_id in range(n_clusters):
        # Count the number of points in each cluster
        num_points = np.sum(labels == cluster_id)
        centroid = cluster_centers[cluster_id]
        NP.append(num_points)
        print(f'Centroid of cluster {cluster_id}: {centroid}, Number of points: {num_points}')

    # Plot the clusters
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(sat_img, cv2.COLOR_BGR2RGB))
    for cluster_id in range(n_clusters):
        cluster_mask = (labels == cluster_id)
        cluster_points = land_pixels[cluster_mask]
        plt.scatter(cluster_points[:, 1], cluster_points[:, 0], s=2, alpha=0.02, label=f'Cluster {cluster_id}')

    # Plot the cluster centers with a unique marker
    for i, center in enumerate(cluster_centers):
        plt.scatter(center[1], center[0], c='red', marker='x', s=100, label=f'Houses {NP[i]}')

    
    plt.savefig(f'plots/{cn}_plot.png',dpi=300, bbox_inches='tight', transparent=True)
    plt.show()

    return tuple(cluster_centers),NP

def make_cluster_land(img_path,satellite_path):
# Load the segmented image
    image = cv2.imread(img_path)
    sat_img=cv2.imread(satellite_path)
    # Define the color range for yellow and dark yellow in HSV
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    lower_dark_yellow = np.array([15, 100, 100])
    upper_dark_yellow = np.array([25, 255, 255])

    # Convert the image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Create masks for yellow and dark yellow
    mask_yellow = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
    mask_dark_yellow = cv2.inRange(hsv_image, lower_dark_yellow, upper_dark_yellow)

    # Combine masks
    mask = cv2.bitwise_or(mask_yellow, mask_dark_yellow)

    # Find the coordinates of the land pixels
    land_pixels = np.column_stack(np.where(mask > 0))

    # Apply DBSCAN clustering
    db = DBSCAN(eps=8, min_samples=1).fit(land_pixels)
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

    print(f'Estimated number of clusters: {n_clusters}')

    # Extract the coordinates of the cluster centers
    cluster_centers = []
    for cluster_id in range(n_clusters):
        cluster_points = land_pixels[labels == cluster_id]
        centroid = cluster_points.mean(axis=0)
        cluster_centers.append(centroid)
        print(f'Centroid of cluster {cluster_id}: {centroid}')

    cluster_centers = np.array(cluster_centers)

    # Plot the clusters
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(sat_img, cv2.COLOR_BGR2RGB))
    for cluster_id in range(n_clusters):
        cluster_mask = (labels == cluster_id)
        cluster_points = land_pixels[cluster_mask]
        plt.scatter(cluster_points[:, 1], cluster_points[:, 0], s=0.1, alpha=0.3,label=f'Cluster {cluster_id}')

    # Plot the cluster centers with a unique marker
    for i, center in enumerate(cluster_centers):
        plt.scatter(center[1], center[0], c='red', marker='x', s=100, label=f'Center {i}')

    # plt.legend()
    # plt.savefig('clustered_image.png', dpi=300, bbox_inches='tight')

    plt.show()
    
    return tuple(cluster_centers)


# Call the function with the path to your images and number of clusters you want
# make_cluster("seg_ss/mumbai.png", "seg_ss/satellite/mumbai.png", n_clusters=10)
# make_cluster_land("seg_ss/bhopal.png", "seg_ss/satellite/bhopal.png")