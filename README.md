# Landmarks_Literature_DB
A webapp to facilitate summarizing literature on landmarks


DB-Naming-Conventions for this app:

table names: lowercase with _ between words, plural

column names: lowercase with _ between words, singular

primary key: [tablename in singular]_id

foreign key: the column name: ref_[singular tablename of the table from which is being referenced]_to_[singular tablename of the table which is referenced]_, so a foreign key referencing the table papers from the table categories would be called ref_category_to_paper, the foreign key name: replace ref by fk
