Features :

* Monitoring several folders, allowing to publish data contained inside
  * Each folder must have a public folder in it (root only writing right)
  * Data will be moved/copied to the public folder when published
* An unique ID for each published file
* Web interface to visualize/download the data
* Baricadr integration to pull the data if it's missing

Workflow should be as follows :

1. An user publish its data with an API call (or CLI (TBA...))
2. The file is copied/moved to the public folder. The hash is computed, and an unique ID is generated. (Optionally, the user will be notified by mail)
3. The data is accessible at BASEURL/data/<data_id> with a web UI (including size, owner, hash)
4. The data can be downloaded at BASEURL/data/download/<data_id>
5. (Optional) If the repo is managed by baricadr and data is missing, the data can be pulled with BASEURL/data/pull/<data_id>


Repos configuration (example in test-data/sample_repos.yml)

`Repo path`: Path to the managed repository
`public_folder`: Path to the public folder of the managed repository
`copy_data`: If set to True, the data will be copied when published. Else, it will be moved, and a symlink will be created
`has_baricadr`: Whether the repository is managed by baricadr. Users will be able to pull the data from the web UI if set to true
