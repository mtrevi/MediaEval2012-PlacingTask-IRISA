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

Pre-Processing:
=====

Code about the technique:

Libraries:

