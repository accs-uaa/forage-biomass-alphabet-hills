# Instructions for Google Cloud Data Management

*Author*: Timm Nawrocki, Alaska Center for Conservation Science

*Last Updated*: 2022-01-04

*Description*: This document contains instructions and commands for moving data between a local machine and a storage bucket on Google Cloud. Cloud storage can be linked to Google Earth Engine (GEE), allowing the ingestion of large datasets into GEE. Data can also be loaded into cloud storage for access by virtual machine processors on Compute Engine. Most of the Google Cloud Compute Engine configuration can be accomplished using the browser interface, which is how configuration steps are explained in this document. If preferred, all of the configuration steps can also be scripted using the Google Cloud SDK. Users should download and install the [Google Cloud SDK](https://cloud.google.com/sdk/) regardless because it is necessary for batch file uploads and downloads.

The following instructions can be used for any data but are targeted to raster datasets over 10 GB. For vector shapefiles or raster datasets under 10GB, the asset upload tool in the [Google Earth Engine code editor](https://code.earthengine.google.com) can be used instead.

## 1. Configure project

Create a new project if necessary and enable API access for Google Cloud Compute Engine. Projects on Google Cloud provide a way to organize similar resource needs and should be more general than the specific funded work project. This document uses the "accs-geospatial-processing" project.

Navigate to the Google Cloud Platform APIs & Services menu for the project and enable the Google Earth Engine, Google Drive, and Compute Engine APIs if not already enabled.

### Create a storage bucket for the project

Create a new storage bucket. Select "Multiregional" and make the multiregion the same as your local machine location. Data can be accessed across regions regardless of which "multiregion" is selected. Select "standard" for storage type. If uploading private data, then select the option to enforce public access prevention.

## 2. Data upload

Open the Google Cloud SDK Shell as an administrator. Prior to other actions, perform an update on the software. Follow the prompts as necessary to update.

```
gcloud components update
```

If this is your first time using Google Cloud SDK, then you will need to authenticate using the following command and then following the in-browser prompts.

```
gcloud auth login
```

Use the "gsutil cp -r" command in Google Cloud SDK to copy data to and from the bucket using the syntax in the example below.

```
gsutil cp -r gs://beringia/example/* ~/example/
```

We upload an image composite for segmentation:

```
gsutil cp -r N:/ACCS_Work/Projects/VegetationEcology/EPA_Chenega/Data/Data_Input/imagery/maxar/composite/Chenega_MaxarComposite_AKALB.tif gs://chenega-wetlands/gee-assets/
```

Once the data have been uploaded to the Compute storage bucket, they can be ingested in GEE.

## 3. Data ingestion

Download and install the [Anaconda distribution of Python](https://www.anaconda.com/products/individual) (or another distribution). The Google Cloud and Earth Engine APIs should be installed into Python from the Anaconda Prompt (while running as administrator) or other console.

```
pip install google-api-python-client
pip install earthengine-api
```

Once installed, the Python client must authenticate to Google's servers using the following command. The authentication process will open a browser window with an authentication code for the user to paste back into the command prompt.

```
earthengine authenticate
```

The Python client provides a local endpoint for working with data hosted in Google Cloud. To move raster data in a Google Cloud storage bucket into an Earth Engine image asset, the following command in the terminal initiates the task. Tasks can take several hours to complete. To track the status of a task, navigate to the [Earth Engine Task Manager](https://code.earthengine.google.com/tasks).

```
earthengine upload image --asset_id=projects/accs-geospatial-processing/assets/chenega_imagery gs://chenega-wetlands/gee-assets/Chenega_MaxarComposite_AKALB.tif
```

Once the tasks complete, the user should be able to import the asset into scripts in Google Earth Engine. Google provides detailed documentation of the upload commands for the [Earth Engine API](https://developers.google.com/earth-engine/guides/command_line#upload).