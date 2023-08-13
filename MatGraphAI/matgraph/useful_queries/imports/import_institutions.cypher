:auto USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/MaxDreger92/MatGraphAI/master/mat2devplatform/matgraph/data/metadata/institutions.csv' AS row
CREATE (institution:Institution{
  ROI: row.`id`,
  name: row.`name`,
  type: row.`types_0`,
  wikipedia_url: row.`wikipedia_url`,
  link: row.`links_0`,
  acronym: row.`acronyms_0`,
  uid: randomUUID(),
  date_added: date()
})

MERGE(country:Country {name: row.`country_country_name`,
                       abbreviation: row.`country_country_code`,
                      date_added: date()})
ON CREATE
SET country.uid = randomUUID()

MERGE(institution)-[:IN]->(country)
 