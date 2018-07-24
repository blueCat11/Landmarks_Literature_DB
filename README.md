# Landmarks_Literature_DB
A webapp to facilitate summarizing literature on landmarks


DB-Naming-Conventions for this app:

table names: lowercase with _ between words, plural
column names: lowercase with _ between words, singular
primary key: [tablename in singular]_id
foreign key: ref_[singular tablename of the table which is referenced]_[singular tablename of the table from which is being referenced], so a foreign key referencing the table papers from the table categories would be called ref_paper_category
