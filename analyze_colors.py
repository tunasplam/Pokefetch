"""
Iterate through ALL of the images and figure out what the key 8
colors for each is. Save them in a nice dataframe to distribute with
PokeFetch.

How to get the 8 best colors? Going to try some clustering algorithms
just for fun.

NOTE the issue here seems to be that there are not enough distinct
colors to run a clustering algorithm.

We may have to do like a ranking where we count how many times each
color occurs and roll off of that.
"""

import matplotlib.pyplot as plt
import numpy as np
from os import listdir, system
from PIL import Image
from pprint import pprint
from sklearn.cluster import KMeans, AgglomerativeClustering
from statistics import mean
from sys import exit

def main():

    # iterate through images in imgs/
    for img_name in listdir('imgs/'):
        img_name = '25_Male.png'
        print(img_name) 

        # infer details about pokemon from filename
        split_name = img_name.split('_')
        if len(split_name) == 2:
            shiny = False
        else:
            shiny = True

        gender = split_name[1]

        im = Image.open('imgs/' + img_name).convert('RGB')
        c_matrix = np.array(im)

        # need to flatten out one of the dims
        c_matrix = c_matrix.reshape(
            c_matrix.shape[0] * c_matrix.shape[1],
            c_matrix.shape[2]
        )
    
        output_colors = ranking(c_matrix)
        print(output_colors)
        print(type(output_colors))
        print(type(output_colors[0][0]))
        # now take the output colors and create them into a grid for
        # printing for inspection.
        output_im = Image.fromarray(output_colors, mode='RGB')
        output_im.save('temp.png')

        #plot_c_matrix(c_matrix)

        break

def kmeans_clustering(c_matrix):

    kmeans = KMeans(n_clusters=8, n_init=10).fit(c_matrix)
    output_colors = kmeans.cluster_centers_

    return output_colors.reshape(1, 8, 3)

def agglo_clustering(c_matrix):
    """
    Ward -> closer but no cigar
    average -> terrible

    """
    ward = AgglomerativeClustering(
        n_clusters=8,
        linkage='ward'
    ).fit(c_matrix)

    # for ward, try classifying the cluster of each pixel
    # and then finding the average of all of the colors in each
    # cluster to create the cluster color.
    output_colors = np.zeros((1, 8, 3))
    for cluster_num in range(8):
        # use this to get the indexes of the colors you want to
        # average
        indexes = ward.labels_ == cluster_num
        r, g, b = 0, 0, 0
        num_colors = 0
        for color in c_matrix[indexes]:
            num_colors += 1
            r += color[0]
            g += color[1]
            b += color[2]

        output_colors[0][cluster_num] = [r/num_colors, g/num_colors, b/num_colors]

    return output_colors

def ranking(c_matrix):

    # could use np.unique to do this but
    # the problem with this approach is that it takes the individual
    # rgb values rather than treating them as one object
    #unique, counts = np.unique(c_matrix, return_counts=True)
    #print(np.asarray(((unique, counts))).T)

    c_matrix = list(c_matrix)

    c_counts = {}
    for arr in c_matrix:
        # np arrays unhashable so convert to tuple
        arr = tuple(arr)
        if arr not in c_counts:
            c_counts[arr] = 1
        else:
            c_counts[arr] += 1

    # kill (0,0,0) since it will always overwhelm
    # filter out (255, 255, 255) since we will always add it
    del c_counts[(0,0,0)]
    del c_counts[(255,255,255)]

    # sort the items in the dict by frequency
    s = sorted(c_counts.items(), key=lambda x: x[1])[::-1]
    # this sorts the key/value pairs of the dict so that the pairs
    # closest to the mean of the values are at indexes 0 and 1.
    a = sorted(c_counts.items(), key=lambda item: abs(item[1] - mean(c_counts.values())))

    output_colors = np.zeros((1, 8,3))
    # output colors will be:
    # black
    output_colors[0][0] = np.array([0,0,0])

    # two most dominant
    print(s)
    print(a)
    output_colors[0][1] = np.array(s[0][0])
    output_colors[0][2] = np.array(s[1][0])
    
    # two most average
    output_colors[0][3] = np.array(a[0][0])
    output_colors[0][4] = np.array(a[1][0])

    # two least common
    output_colors[0][5] = np.array(s[-2][0])
    output_colors[0][6] = np.array(s[-1][0])

    # white
    output_colors[0][7] = np.array([255,255,255])

    return output_colors

def plot_c_matrix(c_matrix):
    fig = plt.figure(figsize=(12,12))
    ax = fig.add_subplot(projection='3d')
    # this lets you select the columns of the matrix
    ax.scatter(c_matrix[:, 0], c_matrix[:, 1], c_matrix[:, 2])
    plt.show()

main()