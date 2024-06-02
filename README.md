# BI_deletion (Babrexit)
A web based system to handle data management issues which arise when an individual leaves the institute.

Intended Action:
==================

1. Notification that a user has left the insitute (e.g. through failure to deliver notifications)
2. Search for all files belonging to that user on home/scratch/group directories
3. Filter these outputs to remove files which are not relevant to scienfic data e.g. files in python environments
4. Use this filtered list as input to a web-based interface and notify user's group leader
5. Group leader reviews and marks files that should be retained
6. This output is passed to a script which then moves files to be retained to location group leader can access and deletes all remaining files.
