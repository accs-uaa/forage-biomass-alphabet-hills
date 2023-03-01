# ---------------------------------------------------------------------------
# Calculate and plot correlation
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2022-01-14
# Usage: Script should be executed in R 4.1.0+.
# Description: "Calculate and Plot Correlation" creates a plot of correlation values for all pairwise covariate combinations on the observed and random paths.
# ---------------------------------------------------------------------------

# Define round date
round_date = 'round_20220105'

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input data
data_folder = paste(drive,
                    root_folder,
                    'Projects/WildlifeEcology/Moose_AlphabetHills/Data',
                    sep = '/')
input_file = paste(data_folder,
                   'Data_Input/training_data',
                   'AllPoints_ExtractedCovariates.csv',
                   sep = '/')

# Define output files
output_plot = paste(data_folder,
                    'Data_Output/model_results',
                    round_date,
                    'covariate_correlation.jpg',
                    sep = '/')
output_csv = paste(data_folder,
                   'Data_Output/model_results',
                   round_date,
                   'covariate_correlation.csv',
                   sep = '/')

# Import libraries
library(dplyr)
library(ggplot2)
library(ggcorrplot)
library(ggtext)
library(RColorBrewer)
library(tibble)
library(tidyr)

# Import data to data frame
point_data = read.csv(input_file)

# Select covariates from point data
point_data = point_data %>%
  select(aspect, elevation, exposure, heat_load, position, radiation, roughness, slope,
         surface_area, surface_relief, wetness,
         maxr_01_blue, maxr_02_green, maxr_03_red, maxr_04_nearir, maxr_evi2, maxr_ndvi, maxr_ndwi,
         maxr_01_blue_std, maxr_02_green_std, maxr_03_red_std, maxr_04_nearir_std,
         maxr_evi2_std, maxr_ndvi_std, maxr_ndwi_std,
         vh, vv,
         s2_06_02_blue, s2_06_03_green, s2_06_04_red, s2_06_05_rededge1, s2_06_06_rededge2,
         s2_06_07_rededge3, s2_06_08_nearir, s2_06_08a_rededge4, s2_06_11_shortir1, s2_06_12_shortir2,
         s2_06_evi2, s2_06_nbr, s2_06_ndmi, s2_06_ndsi, s2_06_ndvi, s2_06_ndwi,
         s2_07_02_blue, s2_07_03_green, s2_07_04_red, s2_07_05_rededge1, s2_07_06_rededge2,
         s2_07_07_rededge3, s2_07_08_nearir, s2_07_08a_rededge4, s2_07_11_shortir1, s2_07_12_shortir2,
         s2_07_evi2, s2_07_nbr, s2_07_ndmi, s2_07_ndsi, s2_07_ndvi, s2_07_ndwi,
         s2_08_02_blue, s2_08_03_green, s2_08_04_red, s2_08_05_rededge1, s2_08_06_rededge2,
         s2_08_07_rededge3, s2_08_08_nearir, s2_08_08a_rededge4, s2_08_11_shortir1, s2_08_12_shortir2,
         s2_08_evi2, s2_08_nbr, s2_08_ndmi, s2_08_ndsi, s2_08_ndvi, s2_08_ndwi,
         s2_09_02_blue, s2_09_03_green, s2_09_04_red, s2_09_05_rededge1, s2_09_06_rededge2,
         s2_09_07_rededge3, s2_09_08_nearir, s2_09_08a_rededge4, s2_09_11_shortir1, s2_09_12_shortir2,
         s2_09_evi2, s2_09_nbr, s2_09_ndmi, s2_09_ndsi, s2_09_ndvi, s2_09_ndwi) %>%
  drop_na()

# Calculate correlation and significance
correlation = round(cor(point_data), 2)
correlation_orig = round(cor(point_data), 2)
sig_matrix = cor_pmat(point_data)

# Plot the correlation
plot = ggcorrplot(correlation,
                  hc.order = TRUE,
                  type = 'lower',
                  outline.color = 'white',
                  ggtheme = ggplot2::theme_minimal,
                  colors = c("#3f7f93", "white", "#e06871"),
                  lab = TRUE,
                  lab_size = 2.5
                  ) +
  theme(axis.text.x = element_markdown(),
        axis.text.y = element_markdown())
plot

# Export plot
ggsave(output_plot,
       plot = plot,
       device = 'jpeg',
       path = NULL,
       scale = 1,
       width = 32,
       height = 24,
       units = 'in',
       dpi = 600,
       limitsize = TRUE)

# Pivot to long form
correlation_data = as.data.frame(correlation_orig) %>%
  rownames_to_column() %>%
  rename(covariate_1 = rowname) %>%
  pivot_longer(!covariate_1, names_to = 'covariate_2', values_to = 'correlation') %>%
  mutate(self_correlate = ifelse(covariate_1 == covariate_2, 1, 0)) %>%
  filter(self_correlate == 0) %>%
  select(covariate_1, covariate_2, correlation)

# Export to csv
write.csv(correlation_data, file = output_csv, fileEncoding = 'UTF-8', row.names = FALSE)