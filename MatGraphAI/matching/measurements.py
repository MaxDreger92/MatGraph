from django.template.loader import render_to_string
from neomodel import db

from matching.config import QUERY_SIMILAR_SKILLS, ABSOLUTE_MINIMUM_SCORE_THRESHOLD, \
    QUERY_SIMILAR_SKILLS_FOR_REPORT, QUERY_FORMAT_SKILL_OVERLAP, SIMILARITY_CORRECTION, SKILL_RELEVANCE_CORRECTION
from matching.matcher import Matcher


QUERY_OCCUPATIONS_BY_SKILLS = f'''
    MATCH
      (occupation:OntologyOccupation)<-[rel:RELEVANT_FOR]-(skill)
    WHERE rel.relevance>=5
    WITH
      DISTINCT occupation,
      SUM(
        ({SKILL_RELEVANCE_CORRECTION('rel.relevance')}) * weight
      ) as weight
    MATCH
      (occupation)<-[rel:RELEVANT_FOR]-(:Skill)
    WHERE rel.relevance>=5
    WITH
      DISTINCT occupation,
      weight / SUM({SKILL_RELEVANCE_CORRECTION('rel.relevance')}) as score
'''

QUERY_OCCUPATION_SKILL_OVERLAP = f'''
    MATCH
      (occupation:OntologyOccupation {{uid: $uid}})<-[rel:RELEVANT_FOR]-(skill)
    WITH
        skill, weight,
        rel.relevance as relevance,
        source_skills
    {QUERY_FORMAT_SKILL_OVERLAP}
'''

OCCUPATION_QUERY = f'''
    {QUERY_SIMILAR_SKILLS}
    
    {QUERY_OCCUPATIONS_BY_SKILLS}
    WHERE score > {ABSOLUTE_MINIMUM_SCORE_THRESHOLD} $company_filter
    
    WITH occupation, score
    ORDER BY score DESC
    
    MATCH (skill:Skill) WHERE skill.uid in $skill_uids
    WITH occupation, score, collect(skill) as occupation_skills
    CALL {{
        WITH
        occupation, occupation_skills
        MATCH
        (skill:Skill)-[:RELEVANT_FOR]->(occupation),
        (skill)-[:SIMILAR]-(profile_skill)
        WHERE
        profile_skill IN occupation_skills AND
        skill.type<>"social"
        WITH collect(skill) as relevant_occupation_skills, occupation
        MATCH
        (skill:Skill)-[:RELEVANT_FOR]->(occupation)
        WHERE NOT skill IN relevant_occupation_skills
        RETURN
        collect(DISTINCT skill.label) as missing_skills
    }}
    CALL {{
        WITH
            occupation, occupation_skills
        MATCH
            (skill:Skill)-[rel:RELEVANT_FOR]->(occupation)
        WHERE
            skill IN occupation_skills AND skill.type<>"social"
        WITH 
            skill
        ORDER BY rel.relevance DESC
        RETURN
            collect(skill.label) as full_matches
    }}
    CALL {{
        WITH
        occupation, full_matches, occupation_skills
        MATCH
            (skill:Skill)-[rel:SIMILAR]-(relevant_skill:Skill)-[occ_rel:RELEVANT_FOR]->(occupation)
        WHERE
            skill IN occupation_skills AND
            (NOT relevant_skill.label IN full_matches) AND skill.type<>"social"
        WITH
            relevant_skill,
            ({SKILL_RELEVANCE_CORRECTION('occ_rel.relevance')})*{SIMILARITY_CORRECTION('rel.similarity')} as relevance
        WITH
            DISTINCT relevant_skill as relevant_skill,
            SUM(relevance) as relevance
        ORDER BY relevance DESC
        RETURN
        collect(relevant_skill.label) as relevant_skills
    }}
    
    WITH occupation, full_matches, relevant_skills, missing_skills, score

    // temporary fix to remove bad ESCO-results...
    WHERE (NOT occupation.skills_generated_from_esco) OR SIZE(full_matches) >= 3 

    RETURN
        occupation.label as label,
        occupation.uid as uid,
        full_matches,
        relevant_skills,
        missing_skills,
        EXISTS((:JobAdvert {{active: true}})-[:IS]->(occupation)) as has_open_positions,
        score
        
    $pagination
'''


# supports filtering for occupations of a specific company
class OccupationMatcher(Matcher):

    type = 'occupation'

    def __init__(self, profile, company_uid=None, **kwargs):
        self.profile = profile
        self.company_uid = company_uid
        super().__init__(**kwargs)

    def build_query_params(self):
        return {
            'skill_uids': [skill.uid for skill in self.profile.get('skills', [])]
        }

    def build_query(self):
        return OCCUPATION_QUERY.replace(
            '$company_filter',
            f"AND EXISTS((occupation)<-[:IS]-(:JobAdvert)<-[:HAS_OPEN_POSITION]-(:Company {{uid: '{self.company_uid}'}}))" if self.company_uid else ''
        ), self.build_query_params()

    def build_result(self):
        return [
            {
                'label': row[0],
                'uid': row[1],
                'skill_overlap': {
                    'matches': row[2],
                    'relevant': row[3],
                    'missing': row[4]
                },
                'has_open_positions': row[5]
            }
            for row in self.db_results
        ]

    def build_extra_reports(self):

        for result in self.result:

            rows, columns = db.cypher_query(f'''
                {QUERY_SIMILAR_SKILLS_FOR_REPORT}
                {QUERY_OCCUPATION_SKILL_OVERLAP}
                ''', {
                    **self.build_query_params(),
                    'uid': result['uid']
                }
            )

            self.report += render_to_string('reports/results.html', {
                'label': result['label'],
                'columns': columns,
                'rows': rows
            })
