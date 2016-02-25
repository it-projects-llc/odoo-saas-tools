SaaS Server Backup S3
=============================

Installed on server and sends backup data to S3. 

To Use:
-------
* Install boto (pip install boto)
* Optionally install FileChunkIO as it provides huge performance boost (pip install filechunkio)
* Enter your AWS ID & KEY
* Enter your AWS bucket in which you want data stored
* Ensure that the bucket exists


TODO
----
use FileChunkIO and boto parrallel processing to handle large files
