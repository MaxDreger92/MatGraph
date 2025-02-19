import os
import sys

from dotenv import load_dotenv

from matgraph.models.ontology import EMMOMatter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import setup_django
load_dotenv()
from importing.OntologyMapper.OntologyMapper import OntologyMapper


# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


ontology_mapper = OntologyMapper("", "matter", EMMOMatter)

ontology_mapper.map_name("Pt particles")
