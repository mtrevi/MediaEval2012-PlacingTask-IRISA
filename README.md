MediaEval2012-PlacingTask-IRISA
===============================

The task requires participants to automatically assign latitude and longitude coordinates to each of the provided test videos. This kind of geographical location tag, or geotag, helps users localize videos, allowing their media to be anchored to real world locations. Currently, however, most videos online are not labelled with this kind of data. This task encourages participants to find innovative ways of doing this labelling automatically. The data comes from Flickr, an example of a photo sharing website that allows users to both encode their photos and videos with geotags, as well as use them when searching and browsing. This paper describes the task, the data sets provided and how the individual participants results are evaluated.

Official Website: http://www.multimediaeval.org/mediaeval2012/placing2012/index.html

Originally, the code was not prepared to be shared, we are sorry if something is not clear or well explained. 

Our Contribution
===============================

We present two different tag-based techniques. Both first pre-select a geographic area of interest and then perform a deeper analysis inside the selected area(s) to return the coordinates more likely to be related with the input tags. In addition, we also implement a content-based method that uses aggregated local images descriptors (VLAD) to find the video’s visual nearest neighbors and infer its coordinates. In this work we do not use gazetteers or any other external information.

Code Structure of 1st run (Sec.2.2)
===============================

=== Pre-Processing ===
* all_convertFlickrDataIntoTxtFormat.py: Converts from Flickr image data to our input structured file
* all_convertVideoXmlIntoTxtFormat.py: Converts from Flickr video XML to our input structured file
* all_computeUsersCommonestPlace.py: Computes users location based on their previous uploads
* all_computeSocialUsersCommonestPlace.py: Computes users location based on their social connections
* all_computePriorProbability.py: Computes the prior-location which is the medoid of all the coordinates in Ttrain.

=== Code about the technique ===
* m1_convertDatasetsIntoDBformat.py: Creates an index of the input file in order to improve the speed
* m1_filteringStopwordListFromDataset_NewMtags.py: Filters tags present in the stop-words list
* m1_filteringTrainingSetWithGeoSpreading.py: Filters tags based on the geo-spreading
* m1_systemTagsBasedLocationRecognition.py: Applies the method of the 1st run

=== Libraries ===
* geoUtils.py: Various methods (coordinates manipulations, serialization of data, etc.)
* objects/FlickrMediaData.py
* objects/ResCandidates.py
* objects/TagInfoClusters.py
* objects/TagInfoCoordinates.py
