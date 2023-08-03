:auto USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/MaxDreger92/MatGraphAI/master/mat2devplatform/matgraph/data/metadata/researchers.csv' AS row
MERGE (researcher:Researcher{
  ORCID: row.`ORCID`,
  last_name: row.`last_name`,
  first_name: row.first_name,
  date_of_birth: row.date_of_birth,
  date_added: row.date_added,
  field: row.field,
  academic_title: row.title,
  uid: randomUUID(),
  name: row. first_name + " " + row.last_name
})
WITH researcher, row
MATCH(country:Country {name: row.`country`})
MATCH(institution:Institution {name: row.`institution`})


MERGE(researcher)-[:IN]->(country)
MERGE(researcher)-[:AFFILIATED_TO]->(institution)

