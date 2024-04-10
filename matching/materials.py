from django.template.loader import render_to_string
from neomodel import db

from matching.config import OVERALL_SCORE_THRESHOLD, QUERY_SIMILAR_SKILLS_WITH_RELEVANCE, REPORT_WEIGHT
from matching.matcher import Matcher
from workprofiles.models import WorkProfile, ExternalWorkProfile
from jobs.models import JobAdvert


def get_total_relevance_from_db(job, minimum_relevance=1):
    results, meta = job.cypher(f'MATCH (job)-[rel:REQUIRES]->(skill:Skill) WHERE ID(job)=$self AND NOT(skill.user_skill=true) AND rel.relevance>={minimum_relevance} RETURN SUM(rel.relevance)')
    return results[0][0]

def get_total_relevance_from_array(skills, minimum_relevance=1):
    return sum([
        skill.relevance if skill.relevance >= minimum_relevance else 0
        for skill in filter(lambda s: not s.user_skill, skills)
    ])

def get_skill_relevances(job, minimum_relevance=1):
    results, meta = job.cypher(f'MATCH (job)-[rel:REQUIRES]->(skill:Skill) WHERE ID(job)=$self AND rel.relevance>={minimum_relevance} RETURN skill.uid, rel.relevance')
    return dict([(skill[0], skill[1]) for skill in results])

def get_skill_relevances_for_occupation(occ):
    results, meta = occ.cypher('MATCH (occ)<-[rel:RELEVANT_FOR]-(skill:Skill) WHERE ID(occ)=$self RETURN skill.uid, rel.relevance')
    return dict([(skill[0], skill[1]) for skill in results])

def get_total_relevance_from_db_for_occupation(occ):
    results, meta = occ.cypher('MATCH (occ)<-[rel:RELEVANT_FOR]-(skill:Skill) WHERE ID(occ)=$self AND NOT(skill.user_skill=true) RETURN SUM(rel.relevance)')
    return results[0][0]


# for some reason, using apoc.coll.min here instead of CASE/WHEN is a serious performance
# bottleneck on production.
# TODO: find out why
QUERY_PROFILES_BY_SKILLS = f'''
    MATCH
      (profile:WorkProfile)-[:HAS_SKILL]->(similar_skill)
    WITH
      DISTINCT profile.uid+source_skill.uid as combo,
      CASE
        WHEN SUM(weight) < $skill_relevances[source_skill.uid]
        THEN SUM(weight)
        ELSE $skill_relevances[source_skill.uid]
      END as weight,
      profile as profile
    WITH
      DISTINCT profile,
      SUM(weight) / apoc.coll.sum([k IN KEYS($skill_relevances) | $skill_relevances[k]]) as score 
'''


QUERY_CANDIDATE_SKILL_OVERLAP_REPORT = f'''
    MATCH
      (profile:WorkProfile {{uid: $uid}})-[rel:HAS_SKILL]->(similar_skill)
    RETURN
        DISTINCT source_skill.label,
        $skill_relevances[source_skill.uid] as relevance,
        {REPORT_WEIGHT('apoc.coll.min([SUM(weight), $skill_relevances[source_skill.uid]])')} as total_weight,
        apoc.text.join(collect(similar_skill.label + ' ('+{REPORT_WEIGHT("weight")}+')'), ', ') as similar_skills
'''

def count_candidates_for_job_by_occupation(job):

    occ = job.occupation.single()

    if not occ:
        return 0

    skill_relevances =  get_skill_relevances_for_occupation(occ)
    total_relevance = get_total_relevance_from_db_for_occupation(occ)

    query = f'''
        {QUERY_SIMILAR_SKILLS_WITH_RELEVANCE}
        {QUERY_PROFILES_BY_SKILLS}
        WHERE score > $threshold AND
        (
            (profile.type='external' AND profile.claimed=false) OR
            (profile.type='user' AND EXISTS(profile.user))
        )
        AND profile.max_quota >= $min_quota
        AND profile.min_quota <= $max_quota

        RETURN count(profile)
    '''

    result, meta = db.cypher_query(query, {
        'threshold': OVERALL_SCORE_THRESHOLD,
        'min_quota': job.min_quota,
        'max_quota': job.max_quota,
        'skill_relevances': skill_relevances,
        'total_relevance': total_relevance
    })

    # avoids 0 candidates; statically adds last number of created date (for consistency)
    return result[0][0] + 5 + int(str(job.created)[-1])


# takes either JobAdvertSerializer.validated_data or a JobAvert object (existing db node)
# using validated_data avoids making changes to the db, so matching can be run in a read-transaction
class CandidateMatcher(Matcher):

    type = 'candidate'

    def __init__(
            self,
            job,
            limit=20,
            count=False,
            include_skill_overlap=False,
            include_details=False,
            hard_language_filter=False,
            minimum_relevance=1,
            ignore_cantons=False,
            **kwargs
    ):

        assert not (count and include_skill_overlap), "you can set either count or include_skill_overlap, not both!"
        assert (not include_details) or (include_details and include_skill_overlap), "include_details requires include_skill_overlap"

        self.job = job
        self.limit = limit
        self.count = count
        self.include_skill_overlap = include_skill_overlap
        self.include_details = include_details
        self.minimum_relevance = minimum_relevance
        self.ignore_cantons = ignore_cantons
        self.hard_language_filter = hard_language_filter

        super().__init__(**kwargs)

    def build_query(self):

        in_graph = isinstance(self.job, JobAdvert)

        min_quota = self.job.min_quota if in_graph else self.job['quota']['min']
        max_quota = self.job.max_quota if in_graph else self.job['quota']['max']

        canton_codes = [
            canton.code
            for canton in
            (self.job.cantons.all() if in_graph else self.job['cantons'])
        ]
        skill_relevances = dict([(skill.uid, skill.relevance) for skill in self.job['skills']]) if not in_graph else get_skill_relevances(self.job, self.minimum_relevance)
        total_relevance = get_total_relevance_from_array(self.job['skills'], minimum_relevance=self.minimum_relevance) if not in_graph else get_total_relevance_from_db(self.job, self.minimum_relevance)

        industries = [ind.uid for ind in self.job.industry_experience.all()] if in_graph else [ind['uid'].hex for ind in self.job['industry_experience']]

        for uid, relevance in skill_relevances.items():
            if relevance < self.minimum_relevance:
                skill_relevances.pop(uid)

        query = f'''
                {QUERY_SIMILAR_SKILLS_WITH_RELEVANCE}
                {QUERY_PROFILES_BY_SKILLS} 
                
                WHERE
                    score > $threshold
                WITH profile, score
                
            '''

        # apply hard filters
        query += '''
                MATCH
                    (profile:WorkProfile)
                WHERE
                    (
                        (profile.type='external' AND profile.claimed=false) OR
                        (profile.type='user' AND EXISTS(profile.user))
                    )
                    AND profile.max_quota >= $min_quota
                    AND profile.min_quota <= $max_quota
                WITH profile, score
            '''

        if self.hard_language_filter:
            query += '''
                CALL {
                    MATCH (lang:Skill)
                    WHERE
                        lang.uid IN keys($skill_relevances) AND
                        $skill_relevances[lang.uid] > 10 AND
                        lang.type="language" 
                    RETURN collect(lang) as languages
                }
                MATCH
                    (profile)
                WHERE
                    all(lang IN languages WHERE EXISTS((profile)-[:HAS_SKILL]->(lang)))
                WITH profile, score
            '''

        # canton filtering for non-graph profiles
        # it's way quicker to filter after skill-matching
        if not self.ignore_cantons and len(canton_codes):
            query += '''
                OPTIONAL MATCH
                    (profile)-[:CAN_WORK_IN]->(canton:Canton)
                WITH
                    DISTINCT profile,
                    collect(canton) as cantons,
                    score
                WHERE
                    isEmpty(cantons) OR ANY(canton in cantons WHERE canton.code IN $canton_codes)
                WITH profile, score
            '''

        # ordering
        query += 'ORDER BY score DESC'

        if self.limit and not self.count:
            query += '''
                LIMIT $limit
            '''

        if self.count:
            query += '''
                    RETURN
                        count(profile)
                '''
        else:

            if self.include_skill_overlap:

                query += '''
                        MATCH
                            (skill:Skill)
                        WHERE
                            skill.uid in KEYS($skill_relevances)
                    '''

                # by default, all >10 relevances will be included in 'partial'
                # if there are <4, we fall back to the 4 highest relevances
                fall_back_to_highest_relevances = len(list(filter(lambda r: r>=10, skill_relevances.values()))) < 4

                # can be used to add stars to important skills
                # CASE WHEN is_important THEN " ★" ELSE "" END as label
                # beware: relevant skills use full_matches to avoid duplicates by label

                query += '''
                    WITH profile, score, collect(skill) as job_skills
                    CALL {
                        WITH
                            profile, job_skills
                        UNWIND
                            job_skills AS skill
                        MATCH
                            (skill)
                        WHERE
                            skill in job_skills AND skill.type<>"social" AND skill.type<>"language" AND
                            NOT(skill.user_skill=true) AND
                            not exists((skill:Skill)-[:SIMILAR]-(:Skill)<-[:HAS_SKILL]-(profile))
                        RETURN
                            collect(skill.label) as missing_skills
                    }
                    CALL {
                        WITH
                            profile, job_skills
                        MATCH
                            (skill:Skill)<-[:HAS_SKILL]-(profile)
                        WHERE
                            skill IN job_skills AND skill.type<>"social"
                        WITH
                            skill,
                            $skill_relevances[skill.uid] > 1 as is_important
                        ORDER BY is_important DESC
                        WITH
                            skill.label as label
                        RETURN
                            collect(label) as full_matches
                    }
                    CALL {
                        WITH
                            profile, full_matches, job_skills
                        MATCH
                            (skill:Skill)
                        WHERE
                            skill IN job_skills AND skill.type<>"language" AND skill.type<>"social" ''' + ('AND $skill_relevances[skill.uid] > 10' if not fall_back_to_highest_relevances else 'WITH skill, profile ORDER BY $skill_relevances[skill.uid] LIMIT 8')+'''
                        CALL {
                            WITH skill, profile
                            MATCH (skill)-[rel:SIMILAR]-(relevant_skill:Skill)<-[:HAS_SKILL]-(profile)
                            WHERE ID(skill)<>ID(relevant_skill)
                            WITH DISTINCT relevant_skill as relevant_skill, max(rel.similarity) as similarity
                            ORDER BY similarity DESC
                            LIMIT 5
                            RETURN SUM(similarity) as score, collect(relevant_skill.label) as relevant_skills
                        }
                        WITH skill, score, relevant_skills
                        ORDER BY score DESC
                        RETURN
                            collect({label: skill.label, score: round(apoc.coll.min([score, 1]), 2), matches: relevant_skills}) as partial_nonlanguage_skills
                    }
                    CALL {
                        WITH profile, job_skills
                        UNWIND job_skills as skill
                        WITH skill, profile
                        WHERE skill.type="language"
                        WITH skill, CASE EXISTS((skill)<-[:HAS_SKILL]-(profile)) WHEN true THEN 1.0 ELSE 0.0 END as score
                        RETURN collect({label: skill.label, score: score, matches: []}) as partial_language_skills 
                    }
                    CALL {
                        WITH partial_nonlanguage_skills, partial_language_skills
                        WITH partial_nonlanguage_skills + partial_language_skills as partial_skills
                        UNWIND partial_skills as partial_skill
                        WITH partial_skill
                        ORDER BY partial_skill.score DESC
                        RETURN collect(partial_skill) as partial_skills
                    }
                    CALL {
                        WITH
                            profile, full_matches, job_skills
                        MATCH
                            (skill:Skill)-[:SIMILAR]-(relevant_skill:Skill)<-[:HAS_SKILL]-(profile)
                        WHERE
                            skill IN job_skills AND
                            NOT relevant_skill.label IN full_matches AND relevant_skill.type="knowledge"
                        WITH
                            $skill_relevances[skill.uid] > 1 as is_important,
                            relevant_skill
                        WITH
                            DISTINCT relevant_skill,
                            MAX(is_important) as is_important
                        ORDER BY is_important DESC
                        RETURN
                            collect(relevant_skill.label) as relevant_skills
                    }
                    WITH *
                    WHERE reduce(missing = 0, partial_skill IN partial_skills | missing + CASE partial_skill.score WHEN 0 THEN 1 ELSE 0 END) <= size(partial_skills)/4
                '''
                # last line excludes profiles that have more than 25% of partial_skills completely missing

                if self.include_details:
                    query += """
                    CALL {
                        WITH profile
                        MATCH (profile)-[:STUDIED]->(item:EducationCVItem)-[:IS]->(sub:Subject)
                        WITH DISTINCT sub.label as label, item.title as title
                        WITH CASE title WHEN "" THEN label WHEN null THEN label ELSE title END as subject
                        RETURN collect(subject) as studied_subjects
                    }
                    CALL {
                        WITH profile
                        MATCH (profile)-[:WORKED_AS]->(item:OccupationCVItem)-[:IS_ROLE]->(occ:OntologyOccupation)
                        WITH occ, item
                        ORDER BY item.since DESC
                        WITH DISTINCT occ.label as label, item.title as title
                        WITH CASE title WHEN "" THEN label WHEN null THEN label ELSE title END as occupation
                        RETURN collect(occupation) as occupations
                    }
                    CALL {
                        WITH profile
                        MATCH (profile)-[:WORKED_AS]->(item:OccupationCVItem)
                        RETURN collect(DISTINCT item.company_name) as companies
                    }
                    CALL {
                        WITH profile
                        MATCH (profile)-[:WORKED_IN]->(in:Industry)
                        WITH DISTINCT in
                        WITH in.label + CASE in.uid IN $industries WHEN true THEN " [MATCH]" ELSE "" END as label
                        ORDER BY label
                        RETURN collect(label) as industries
                    }
                    CALL {
                        WITH profile
                        MATCH (profile)-[rel:HAS_SKILL]->(lang:Skill)
                        WHERE lang.type="language"
                        WITH DISTINCT lang, rel.level as level
                        ORDER BY level DESC
                        WITH lang.label + ['', ' (A1)', ' (B)', ' (C1)', ' (C2)'][level] as label
                        RETURN collect(label) as languages
                    }
                    """

                query += """
                RETURN
                    profile,
                    score,
                    full_matches,
                    relevant_skills,
                    partial_skills,
                    missing_skills
                """

                if self.include_details:
                    query += """,
                        studied_subjects,
                        occupations,
                        companies,
                        industries,
                        languages,
                    """

                    # calculates the distance between the two center points
                    # TODO: possible improvement: calculate distance between bounding boxes
                    if in_graph and self.job.location_center:
                        query += f'''
                            toInteger(
                                point.distance(point({{latitude: {self.job.location_center.latitude}, longitude: {self.job.location_center.longitude}, crs: "WGS-84"}}), profile.location)
                            / 1000) as distance_km
                        '''
                    else:
                        query += '"" as distance_km'

            else:
                query += '''
                        RETURN
                            profile,
                            score
                    '''

        params = {
            'min_quota': min_quota,
            'max_quota': max_quota,

            'canton_codes': canton_codes,

            'skill_relevances': skill_relevances,
            'total_relevance': total_relevance,
            'industries': industries,

            'limit': self.limit,
            'threshold': OVERALL_SCORE_THRESHOLD
        }

        return query, params


    def build_result(self):
        if self.count:
            return self.db_results[0][0]

        return [
            {
                'profile': ExternalWorkProfile.inflate(row[0]) if row[0]['type'] == 'external' else WorkProfile.inflate(row[0]),
                'score': row[1],
                'skill_overlap': {
                    'matches': row[2],
                    'relevant': row[3],
                    'partial': row[4],
                    'missing': row[5]
                } if self.include_skill_overlap else None,
                'details': {
                    'studied_subjects': row[6],
                    'occupations': row[7],
                    'companies': row[8],
                    'industries': row[9],
                    'languages': row[10],
                    'distance_km': row[11]
                } if self.include_details else None
            }
            for row in self.db_results
        ]

    def build_results_for_report(self):
        if self.count:
            return self.db_results, self.db_columns

        return [
            [row[0]['uid']]+row[1:]
            for row in self.db_results
        ], self.db_columns


    def build_extra_reports(self):

        if self.count:
            return

        for row in self.db_results:

            rows, columns = db.cypher_query(
                QUERY_SIMILAR_SKILLS_WITH_RELEVANCE + QUERY_CANDIDATE_SKILL_OVERLAP_REPORT,
                {
                    **self.build_query()[1],
                    'uid': row[0]['uid'],
                }
            )
            self.report += render_to_string('reports/results.html', {
                'label': f'{row[0]["uid"]} ({row[1]})',
                'columns': columns,
                'rows': rows
            })
