/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Calculate burn difference
Author: Timm Nawrocki, Alaska Center for Conservation Science
Created on: 2022-03-29
Usage: Must be executed from the Google Earth Engine code editor.
Description: "Calculate burn difference" calculates a 3-year pre-fire median normalized burn ratio (NBR) and a 3-year post-fire NBR and exports the difference between the two.
---------------------------------------------------------------------------*/

// Define an area of interest geometry.
var area_feature = ee.FeatureCollection('projects/accs-geospatial-processing/assets/alphabet_studyarea');

// Set date filters
var filter_before = ee.Filter.or(
  ee.Filter.date('2000-06-20', '2000-08-15'),
  ee.Filter.date('2001-06-20', '2001-08-15'),
  ee.Filter.date('2002-06-20', '2002-08-15'));
var filter_after = ee.Filter.or(
  ee.Filter.date('2005-06-20', '2005-08-15'),
  ee.Filter.date('2006-06-20', '2006-08-15'),
  ee.Filter.date('2007-06-20', '2007-08-15'));

// Define a function to create a cloud-reduction mask and calculate NDVI.
var mask_clouds = function(image) {
  //Get a cloud score in the range [0, 100].
  var cloud_score = ee.Algorithms.Landsat.simpleCloudScore(image).select('cloud');
  //Create a mask of cloudy pixels from an arbitrary threshold.
  var cloud_mask = cloud_score.lte(20);
  // Return the masked image with an NDVI band.
  return image.updateMask(cloud_mask);
};

// Define a function for NDSI calculation.
var add_nbr = function(image) {
  //Compute the Normalized Burn Ratio (NBR).
  var nbr_calc = image.normalizedDifference(['B5', 'B7']).rename('NBR');
  // Return the masked image with an NBR band.
  return image.addBands(nbr_calc);
};

// Import Landsat 8 TOA Reflectance (ortho-rectified).
var l7_TOA = ee.ImageCollection("LANDSAT/LE07/C02/T1_TOA")
  .filterBounds(area_feature);
var l5_TOA = ee.ImageCollection("LANDSAT/LT05/C02/T1_TOA")
  .filterBounds(area_feature);

// 1. CREATE BEFORE COMPOSITE

//Filter the image collections
var l5_before = l5_TOA
  .filter(filter_before)
  .map(mask_clouds)
  .map(add_nbr)
  .select('NBR');
var l7_before = l7_TOA
  .filter(filter_before)
  .map(mask_clouds)
  .map(add_nbr)
  .select('NBR');

// Merge Landsat 5 and 7
var collection_before = ee.ImageCollection(l5_before.merge(l7_before));
var median_before = collection_before
  .median();

// 2. CREATE AFTER COMPOSITE

//Filter the image collections
var l5_after = l5_TOA
  .filter(filter_after)
  .map(mask_clouds)
  .map(add_nbr)
  .select('NBR');
var l7_after = l7_TOA
  .filter(filter_after)
  .map(mask_clouds)
  .map(add_nbr)
  .select('NBR');

// Merge Landsat 5 and 7
var collection_after = ee.ImageCollection(l5_after.merge(l7_after));
var median_after = collection_after
  .median();

// 3. CALCULATE DIFFERENCE

var difference = median_before.subtract(median_after)

// Define parameters.
var nbrParams = {
  bands: ['NBR'],
  min: -1,
  max: 1,
  palette: ['blue', 'white', 'green']
};

// Add image to the map.
Map.addLayer(median_before, nbrParams, 'NBR Before')
Map.addLayer(median_after, nbrParams, 'NBR After')
Map.addLayer(difference, nbrParams, 'Difference')

// Add study area to map
var empty = ee.Image().byte();
var outlines = empty.paint({
  featureCollection: area_feature,
  color: 'red',
  width: 2
});
Map.addLayer(outlines, {palette: 'FFFF00'}, 'Study Area');

// Export image
Export.image.toDrive({
  image: difference,
  description: 'burn_diff',
  folder: 'alphabethills_landsat',
  scale: 30,
  region: area_feature,
  maxPixels: 1e12
});
