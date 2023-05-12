# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Run Linear Regression Model
# Author: Amanda Droghini, Alaska Center for Conservation Science
# Usage: Code chunks must be executed sequentially in R Studio or R Studio Server installation.
# Description: "Explore Data - Preliminary Linear Regression" splits the geo-referenced data into testing (n = 3) and training (n=10) datasets and applies a linear regression model to explore the statistical relationship between distance of geo-referenced centroids from original centroids, and height and speed of the aircraft. The model seems to perform well enough that we are going to pursue building a linear regression model uses leave-one-out cross-validation.
# ---------------------------------------------------------------------------

# Import required libraries
library(tidyverse)

# Set root directory
drive = 'D:'
root_folder = 'ACCS_Work'

# Set desired number of decimal places for coordinates
options(digits = 12)

# Define input folders
project_folder <- paste(drive,root_folder,"Projects/WildlifeEcology/Moose_AlphabetHills/Data", sep = "/")
image_folder <- paste(project_folder, 'Data_Input/imagery/aerial', sep = "/")

# Define input file
input_csv <- paste(image_folder,
                   'AerialImagery_Metadata.csv',
                   sep = '/')

# Read input file
all_metadata <- read_csv(input_csv)

# Explore data ----
# Variables we are interested in are: distance_meters (response), height, speed
plot(distance_meters ~ height, data = all_metadata)
plot(distance_meters ~ speed, data = all_metadata)

# Create testing and training datasets ----
georeferenced_data <- all_metadata %>% 
  subset(!is.na(distance_meters))

# Randomly exclude 3 of the geo-referenced rows to use as test data
test_data <- georeferenced_data %>% 
  slice_sample(n=3, replace=FALSE)

# Train data includes all remaining geo-referenced rows
train_data <- subset(georeferenced_data, !(imageNumber %in% test_data$imageNumber))

# Run linear regression model ----
# Using training data
model_distance <- lm(distance_meters ~ height + speed, data = train_data)

# Predict to test data
predict_distance <- predict(object=model_distance, newdata=test_data)

# Compare predicted results to actual test data
predict_distance
test_data$distance_meters

# Clean workspace
rm(list=ls())