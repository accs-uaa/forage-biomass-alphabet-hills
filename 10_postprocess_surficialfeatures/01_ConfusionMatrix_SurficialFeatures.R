# ---------------------------------------------------------------------------
# Format confusion matrix
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2023-02-22
# Usage: Script should be executed in R 4.1.0+.
# Description: "Format confusion matrix" calculates user's and producer's accuracy.
# ---------------------------------------------------------------------------

# Define version
round_date = 'round_20220607'

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input data
data_folder = paste(drive,
                    root_folder,
                    'Projects/WildlifeEcology/Moose_AlphabetHills/Data',
                    sep = '/')
raw_file = paste(data_folder,
                 'Data_Output/model_results',
                 round_date,
                 'surficial_features/confusion_matrix_raw.csv',
                 sep = '/')

# Define output files
output_file = paste(data_folder,
                    'Data_Output/model_results',
                    round_date,
                    'surficial_features/confusion_matrix.csv',
                    sep = '/')

# Import libraries
library(dplyr)
library(tidyr)

# Import data to data frame
raw_data = read.csv(raw_file)

# Change column and row labels
confusion_matrix = raw_data %>%
  rename(barren = X1, burned = X2, drainage = X3, riparian = X4,
         floodplain = X5, water = X6, uplandlowland = X7, aspen = X8) %>%
  mutate(Actual = case_when(Actual == 1 ~ 'barren',
                            Actual == 2 ~ 'burned',
                            Actual == 3 ~ 'drainage',
                            Actual == 4 ~ 'riparian',
                            Actual == 5 ~ 'floodplain',
                            Actual == 6 ~ 'water',
                            Actual == 7 ~ 'uplandlowland',
                            Actual == 8 ~ 'aspen',
                            TRUE ~ Actual)) %>%
  mutate(acc_producer = 0)

# Calculate user accuracy
count = 1
while (count < 10) {
  confusion_matrix[count, 11] = round(confusion_matrix[count, count + 1] / confusion_matrix[count, 10],
                                      digits = 2)
  count = count + 1
}

# Calculate producers accuracy
confusion_matrix[10, 1] = 'acc_user'
count = 2
while (count < 11) {
  confusion_matrix[10, count] = round(confusion_matrix[count - 1, count] / confusion_matrix[9, count],
                                      digits = 2)
  count = count + 1
}

# Export data
write.csv(confusion_matrix, file = output_file, fileEncoding = 'UTF-8', row.names = FALSE)