############################
#     MATCHING OPTIONS     #
############################

# threshold for prioritizing lead/custom jobs and email recommendations
OVERALL_SCORE_THRESHOLD = 0.35

# this threshold is used for result pages in SkillMatcher and job list pages. lead/custom jobs with > OVERALL_SCORE_THRESHOLD
# will still be shown at the top
ABSOLUTE_MINIMUM_SCORE_THRESHOLD = 0.2

# multiple similarity-matches can never boost a skills relevance over this score
# important to keep scores comparable and <= 1
MAX_SKILL_MATCHING_RELEVANCE = 1.0

# skill relevance calculation factor.
# using an exponential function boosts the relevance of high priority skills
def SKILL_RELEVANCE_CORRECTION(term):
    return f'{term}^3'

def SIMILARITY_CORRECTION(term):
    return f'sqrt({term})'

def REPORT_WEIGHT(term):
    return f'round({term}, 2)'


############################
#     MATCHING QUERIES     #
############################


# for some reason, using apoc.coll.min here instead of CASE/WHEN is a serious performance
# bottleneck on production.
# TODO: find out why
QUERY_SIMILAR_SKILLS = f'''
    MATCH
      (skill:Skill)-[similar:SIMILAR]-(profile_skill:Skill)
    WHERE
      profile_skill.uid IN $skill_uids
    WITH
      DISTINCT skill,
      CASE
        WHEN MAX({SIMILARITY_CORRECTION('similar.similarity')}) > {MAX_SKILL_MATCHING_RELEVANCE}
        THEN {MAX_SKILL_MATCHING_RELEVANCE}
        ELSE MAX({SIMILARITY_CORRECTION('similar.similarity')})
      END as weight
'''

QUERY_SIMILAR_SKILLS_FOR_REPORT = f'''
    {QUERY_SIMILAR_SKILLS},
    collect(
      profile_skill.label +
      " (" +
        {REPORT_WEIGHT(SIMILARITY_CORRECTION('similar.similarity'))}
      + ")"
    ) as source_skills
'''

# corrects for relevance based on $skill_relevances ({skill_uid: relevance}})
QUERY_SIMILAR_SKILLS_WITH_RELEVANCE = f'''
    MATCH
      (skill:Skill)-[similar:SIMILAR]-(similar_skill:Skill)
    WHERE
      skill.uid IN KEYS($skill_relevances)
    WITH
      skill as source_skill,
      similar_skill,
      {SIMILARITY_CORRECTION('similar.similarity')} * $skill_relevances[skill.uid] as weight
'''

############################
#      REPORT QUERIES      #
############################

# inputs: skill, weight, relevance, source_skills
# QUERY_SIMILAR_SKILLS_FOR_REPORT + relevance for matched element
QUERY_FORMAT_SKILL_OVERLAP = f'''
    RETURN
      skill.label as skill,
      relevance,
      {REPORT_WEIGHT('weight')} as source_weight,
      {REPORT_WEIGHT(
        f'({SKILL_RELEVANCE_CORRECTION("relevance")}) * weight'
      )} as weight,
      apoc.text.join(source_skills, ", ") as source_skills
    ORDER BY weight DESC
'''