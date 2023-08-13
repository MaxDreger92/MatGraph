//Import of ontologies, first neosemantic gets initialized, subsequently the ontologies can be imported, each domain gets
//an additional label to "EMMO_DOMAIN" to make the different domains separately accessible
Match (n)-[m]-(r) delete n,m,r;
Match (n) delete n;
CREATE CONSTRAINT UniqueAlternativeLabel IF NOT EXISTS ON (al:Alternative_Label) ASSERT al.name IS UNIQUE;

//CREATE CONSTRAINT n10s_unique_uri FOR (r:Resource) REQUIRE r.uri IS UNIQUE;

call n10s.graphconfig.init({
baseSchemaPrefix:"EMMO",
subClassOfRel:"IS_A"}
);
call n10s.graphconfig.set({handleRDFTypes: "NODES",force:true}) ;

// first pass, load the onto. Note that there are irregular uris, but we accept them with verifyUriSyntax: false
call n10s.rdf.import.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/material.owl", "Turtle") ;
CALL n10s.rdf.stream.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/material.owl", "Turtle") YIELD subject, predicate, object
WHERE predicate CONTAINS "alternative_label"
MATCH (cls:Resource {uri: subject })
MERGE (cls)<-[:IS_ALTERNATIVE_LABEL]-(al:Alternative_Label {name: object});


//CALL n10s.onto.import.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/quantities.owl","RDF/XML", { verifyUriSyntax: false }) ;
//CALL n10s.rdf.stream.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/quantities.owl", "RDF/XML") YIELD subject, predicate, object
//WHERE predicate CONTAINS "alternative_label"
//MATCH (cls:Resource { uri: subject })
//MERGE (cls)<-[:IS_ALTERNATIVE_LABEL]-(al:Alternative_Label {name: object});
//
//call n10s.onto.import.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/manufactured.owl","RDF/XML", { verifyUriSyntax: false }) ;
//CALL n10s.rdf.stream.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/manufactured.owl", "RDF/XML") YIELD subject, predicate, object
//WHERE predicate CONTAINS "alternative_label"
//MATCH (cls:Resource { uri: subject })
//MERGE (cls)<-[:IS_ALTERNATIVE_LABEL]-(al:Alternative_Label {name: object});

call n10s.onto.import.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/manufacturing.owl","RDF/XML", { verifyUriSyntax: false }) ;
CALL n10s.rdf.stream.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/manufacturing.owl", "RDF/XML") YIELD subject, predicate, object
WHERE predicate CONTAINS "alternative_label"
MATCH (cls:Resource { uri: subject })
MERGE (cls)<-[:IS_ALTERNATIVE_LABEL]-(al:Alternative_Label {name: object});

//call n10s.onto.import.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/units.owl","RDF/XML", { verifyUriSyntax: false}) ;
//CALL n10s.rdf.stream.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/units.owl", "RDF/XML") YIELD subject, predicate, object
//WHERE predicate CONTAINS "alternative_label"
//MATCH (cls:EMMO__Class { uri: subject })
//MERGE (cls)<-[:IS_ALTERNATIVE_LABEL]-(al:Alternative_Label {name: object});


// we want named instances to link to the classes imported from the onto, so we change the handleRDFTypes mode.

// second pass to load the owl:Matter
//call n10s.rdf.stream.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/materials.owl","RDF/XML",{ verifyUriSyntax: false , limit :100000}) yield subject, predicate, object
//MATCH (n:Resource{uri:subject})
//SET n:EMMOMatter;
//MATCH (cls:EMMO__Class)
//WHERE EXISTS(cls.alternative_label)
//UNWIND cls.alternative_label AS alt_label
//MERGE (al:Alternative_Label {name: alt_label})
//CREATE (cls)-[:HAS_ALTERNATIVE_LABEL]->(al);
////second pass to load the owl:Matter
//call n10s.rdf.stream.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/manufacturing.owl","RDF/XML", { verifyUriSyntax: false , limit :100000}) yield subject, predicate, object
//MATCH (n:Resource{uri:subject})
//SET n:EMMOProcess;



// second pass to load the owl:Matter
//call n10s.rdf.stream.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/manufacturing.owl","RDF/XML", { verifyUriSyntax: false , limit :100000}) yield subject, predicate, object
//MATCH (n:Resource{uri:subject})
//SET n:EMMOProcess;
//
//call n10s.rdf.stream.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/materials.owl","RDF/XML", { verifyUriSyntax: false , limit :100000}) yield subject, predicate, object
//MATCH (n:Resource{uri:subject})
//SET n:EMMOMatter;
//
//call n10s.rdf.stream.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/quantities.owl","RDF/XML", { verifyUriSyntax: false , limit :100000}) yield subject, predicate, object
//MATCH (n:Resource{uri:subject})
//SET n:EMMOQuantity;

//call n10s.rdf.stream.fetch("https://raw.githubusercontent.com/IEK-13/MatGraphAI/AddCSVAPI/Ontology/units.owl","RDF/XML", { verifyUriSyntax: false , limit :100000}) yield subject, predicate, object
//MATCH (n:Resource{uri:subject})
//WITH n.EMMO__label as label, n.name as name, n
//SET n.EMMO__label = name
//SET n.name = label
//SET n:EMMO_Unit;

//MATCH(n)
//WHERE n:EMMO__Relationship OR n:owl__AnnotationProperty OR n:owl__AllDisjointClasses
//DETACH DELETE n;
//
//MATCH (n)
//WHERE n:Resource OR n:EMMO__Class OR n:owl__Class OR n:owl__Ontology
//REMOVE n:Resource, n:EMMO__Class, n:owl__Class, n:owl__Ontology;


//MATCH (n)
//WHERE (n:EMMOMatter OR n:EMMOProcess OR n:EMMOQuantity OR n:EMMO_Unit) AND (n.uid) IS NOT NULL
//SET n.uid = randomUUID()