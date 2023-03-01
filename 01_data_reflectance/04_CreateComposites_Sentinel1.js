/* -*- coding: utf-8 -*-
---------------------------------------------------------------------------
Median Growing-season Composite Sentinel 1 SAR for 2015-2021
Author: Timm Nawrocki, Alaska Center for Conservation Science
Last Updated: 2022-01-01
Usage: Must be executed from the Google Earth Engine code editor.
Description: This script produces median composites using ascending orbitals for the VV and VH polarizations from Sentinel-1.
---------------------------------------------------------------------------*/

// Define an area of interest geometry.
var area_feature = ee.FeatureCollection('projects/accs-geospatial-processing/assets/alphabethills_studyarea');

// Import the Sentinel-1 Image Collection VV and VH polarizations within study area and date range
var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(area_feature)
    .filter(ee.Filter.calendarRange(2015, 2021, 'year'))
    .filter(ee.Filter.calendarRange(6, 8, 'month'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
    .sort('system:time_start');
print("Sentinel 1 (date-filtered:", s1);

// Create a VV and VH composite from ascending orbits
var vv = s1.select('VV').median()
var vh = s1.select('VH').median()
print(vv)
print(vh)

// Add image to the map.
Map.centerObject(area_feature);
Map.addLayer(vv, {min: -30, max: 0}, 'vv');
Map.addLayer(vh, {min: -30, max: 0}, 'vh');

// Add study area to map
var empty = ee.Image().byte();
var outlines = empty.paint({
  featureCollection: area_feature,
  color: 'red',
  width: 2
});
Map.addLayer(outlines, {palette: 'FFFF00'}, 'Study Area');

// Export images to Google Drive.
Export.image.toDrive({
    image: vv,
    description: 'Sent1_vv',
    folder: 'alphabethills_sentinel1',
    scale: 10,
    region: area_feature,
    maxPixels: 1e12
});
Export.image.toDrive({
    image: vh,
    description: 'Sent1_vh',
    folder: 'alphabethills_sentinel1',
    scale: 10,
    region: area_feature,
    maxPixels: 1e12
});
