import base64
import sys
import os
import tempfile
import uuid
import zipfile
from datetime import date
# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import setup_django

from neo4j_handlers import Neo4jDataRetrievalHandler, SearchHandler

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import streamlit as st
from schema_ingestion.models import SynthesisStep, Material, Technique, Synthesis, Experiment, OrganizationalData, \
    SamplePreparationStep, SamplePreparation, Data, Quantity, PreprocessingStep, Preprocessing

import sys
import os






import sys
import os
from datetime import date

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import streamlit as st
from schema_ingestion.models import (
    SynthesisStep, Material, Technique, Synthesis, Experiment, OrganizationalData,
    SamplePreparation, SamplePreparationStep, Measurement, Metadata,
    Analysis, AnalysisStep,
    # Data, Quantity # If these models exist, import them as needed.
)

def advanced_search_tab_ui():
    st.subheader("Advanced Search with Multiple Criteria")

    # We store the user's input in session_state to allow them to add more fields dynamically
    if "materials" not in st.session_state:
        st.session_state["materials"] = []
    if "techniques" not in st.session_state:
        st.session_state["techniques"] = []
    if "parameters" not in st.session_state:
        st.session_state["parameters"] = []
    if "properties" not in st.session_state:
        st.session_state["properties"] = []
    if "metadata" not in st.session_state:
        st.session_state["metadata"] = []

    # Buttons to add a new search item
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Add Material Filter"):
            st.session_state["materials"].append("")
    with col2:
        if st.button("Add Technique Filter"):
            st.session_state["techniques"].append("")
    with col3:
        if st.button("Add Parameter Filter"):
            st.session_state["parameters"].append("")
    with col4:
        if st.button("Add Property Filter"):
            st.session_state["properties"].append("")
    with col5:
        if st.button("Add Metadata Filter"):
            st.session_state["metadata"].append({"key": "", "value": ""})

    # Render the dynamic lists
    st.markdown("### Materials")
    for i, mat in enumerate(st.session_state["materials"]):
        st.session_state["materials"][i] = st.text_input(
            f"Material Filter #{i+1}",
            value=mat,
            key=f"material_filter_{i}"
        )

    st.markdown("### Techniques")
    for i, tech in enumerate(st.session_state["techniques"]):
        st.session_state["techniques"][i] = st.text_input(
            f"Technique Filter #{i+1}",
            value=tech,
            key=f"tech_filter_{i}"
        )

    st.markdown("### Parameters")
    for i, param in enumerate(st.session_state["parameters"]):
        st.session_state["parameters"][i] = st.text_input(
            f"Parameter Filter #{i+1}",
            value=param,
            key=f"param_filter_{i}"
        )

    st.markdown("### Properties")
    for i, prop in enumerate(st.session_state["properties"]):
        st.session_state["properties"][i] = st.text_input(
            f"Property Filter #{i+1}",
            value=prop,
            key=f"prop_filter_{i}"
        )

    st.markdown("### Metadata")
    for i, md in enumerate(st.session_state["metadata"]):
        col_key, col_value = st.columns(2)
        with col_key:
            st.session_state["metadata"][i]["key"] = st.text_input(
                f"Metadata Key #{i+1}",
                value=md["key"],
                key=f"meta_key_{i}"
            )
        with col_value:
            st.session_state["metadata"][i]["value"] = st.text_input(
                f"Metadata Value #{i+1}",
                value=md["value"],
                key=f"meta_value_{i}"
            )

    # Output format
    adv_output_format = st.selectbox("Choose output format", ["json", "csv"], key="adv_output_format")

    if st.button("Run Advanced Search"):
        # Build the search_instructions dict
        search_instructions = {
            "materials": [m for m in st.session_state["materials"] if m.strip()],
            "techniques": [t for t in st.session_state["techniques"] if t.strip()],
            "parameters": [p for p in st.session_state["parameters"] if p.strip()],
            "properties": [p for p in st.session_state["properties"] if p.strip()],
            "metadata": [
                {"key": md["key"], "value": md["value"]}
                for md in st.session_state["metadata"]
                if md["key"].strip() or md["value"].strip()
            ]
        }
        print("SEARCH INSTRUCTIONS", search_instructions)

        # Use the SearchHandler to find matching experiments
        sh = SearchHandler()
        experiments = sh.search_experiments(search_instructions)

        if not experiments:
            st.warning("No experiments found matching your criteria.")
        else:
            st.success(f"Found {len(experiments)} experiment(s).")
            selected_experiment = st.selectbox(
                "Select an experiment to retrieve data from:",
                options=experiments,
                format_func=lambda e: f"{e.experiment_id} (UID: {e.uid})"
            )

            if st.button("Retrieve Data", key="retrieve_adv"):
                retrieval_handler = Neo4jDataRetrievalHandler()
                experiment_uid = str(selected_experiment.uid)

                # JSON
                if adv_output_format == "json":
                    try:
                        result_str = retrieval_handler.get_experiment_data(
                            experiment_uid=experiment_uid,
                            output_format='json'
                        )
                        st.download_button(
                            label="Download as JSON",
                            data=result_str,
                            file_name=f"experiment_{selected_experiment.experiment_id}.json",
                            mime="application/json"
                        )
                        st.json(result_str)
                    except Exception as e:
                        st.error(f"Error retrieving JSON data: {e}")

                else:  # CSV
                    try:
                        with tempfile.TemporaryDirectory() as tmpdir:
                            result_files = retrieval_handler.get_experiment_data(
                                experiment_uid=experiment_uid,
                                output_format='csv',
                                base_path=tmpdir
                            )
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip_file:
                                with zipfile.ZipFile(tmp_zip_file.name, 'w') as zipf:
                                    for label, filepath in result_files.items():
                                        arcname = os.path.basename(filepath)
                                        zipf.write(filepath, arcname=arcname)

                                zip_bytes = tmp_zip_file.read()

                            b64_zip = base64.b64encode(zip_bytes).decode()
                            href = (
                                f'<a href="data:application/zip;base64,{b64_zip}" '
                                f'download="experiment_{selected_experiment.experiment_id}.zip">Download CSV ZIP</a>'
                            )
                            st.markdown(href, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error retrieving CSV data: {e}")

def define_organizational_data_form():
    st.subheader("Organizational Data")
    experiment_title = st.text_input("Experiment Title", value="Default Experiment Title", max_chars=255,
                                     help="Enter the title of the experiment.", key="experiment_title")
    external_experiment_id = st.text_input("Experiment ID", value="EXP-001", max_chars=50,
                                  help="Enter the unique ID for the experiment.", key="exp_id")
    measurement_id = st.text_input("Measurement ID", value="MEAS-001", max_chars=50,
                                   help="Enter the unique ID for the measurement.", key="measurement_id")
    upload_date = st.date_input("Upload Date", value=date.today(),
                                help="Select the upload date.", key="upload_date")
    measurement_date = st.date_input("Measurement Date", help="Select the date of the measurement.", key="measurement_date")

    # Institution details
    institution = st.text_input("Institution", value="Default Institution", max_chars=255,
                                help="Enter the institution name.", key="institution")
    founding_body = st.text_input("Founding Body", value="Default Founding Body", max_chars=255,
                                  help="Enter the founding body (if applicable).", key="founding_body")
    country = st.text_input("Country", value="Default Country", max_chars=100,
                            help="Enter the country of origin.", key="country")

    # Author details
    author = st.text_area("Author(s)", value="John Doe\nJane Smith",
                          help="Enter author names separated by newlines.", key="author")
    orcid = st.text_area("ORCID(s)", value="0000-0000-0000-0000\n1111-1111-1111-1111",
                         help="Enter ORCID IDs separated by newlines.", key="orcid")
    email = st.text_area("Email(s)", value="john.doe@example.com\njane.smith@example.com",
                         help="Enter email addresses separated by newlines.", key="email")

    # Publication details
    published = st.text_input("Published", value="Not Published", max_chars=50,
                              help="Enter the publication status (if applicable).", key="published")
    publication = st.text_input("Publication", value="Default Publication", max_chars=255,
                                help="Enter the publication name (if applicable).", key="publication")
    doi = st.text_input("DOI", value="10.1234/doi-example", help="Enter the DOI of the publication (if applicable).", key="doi")
    journal = st.text_input("Journal", value="Default Journal", max_chars=255,
                            help="Enter the journal name (if applicable).", key="journal")
    volume = st.text_input("Volume", value="1", max_chars=50,
                           help="Enter the volume of the publication.", key="volume")
    issue = st.text_input("Issue", value="1", max_chars=50, help="Enter the issue of the publication.", key="issue")
    pages = st.text_input("Pages", value="1-10", max_chars=50, help="Enter the pages of the publication.", key="pages")
    publication_date = st.date_input("Publication Date", help="Select the publication date.", key="publication_date")

    # Experiment metadata
    topic = st.text_input("Topic", value="Default Topic", max_chars=255,
                          help="Enter the topic of the experiment.", key="topic")
    device = st.text_input("Device", value="Default Device", max_chars=255,
                           help="Enter the device used in the experiment.", key="device")
    component = st.text_input("Component", value="Default Component", max_chars=255,
                              help="Enter the main component of the experiment.", key="component")
    subcomponent = st.text_input("Subcomponent", value="Default Subcomponent", max_chars=255,
                                 help="Enter any subcomponent details.", key="subcomponent")
    granularity_level = st.text_input("Granularity Level", value="High", max_chars=255,
                                      help="Specify the granularity level.", key="granularity_level")
    format_ = st.text_input("Format", value="CSV", max_chars=50,
                            help="Enter the format of the data or experiment.", key="format")
    file_size = st.number_input("File Size", value=100, min_value=0, step=1, format="%d",
                                help="Enter the file size in positive integers.", key="file_size")
    file_size_unit = st.text_input("File Size Unit", value="MB", max_chars=10,
                                   help="Enter the unit of file size, e.g., MB, KB.", key="file_size_unit")
    file_name = st.text_input("File Name", value="datafile.csv", max_chars=255,
                              help="Enter the file name.", key="file_name")
    dimension_x = st.number_input("Dimension X", value=1024, min_value=0, step=1, format="%d",
                                  help="Enter the X dimension in positive integers.", key="dimension_x")
    dimension_y = st.number_input("Dimension Y", value=768, min_value=0, step=1, format="%d",
                                  help="Enter the Y dimension in positive integers.", key="dimension_y")
    dimension_z = st.number_input("Dimension Z", value=256, min_value=0, step=1, format="%d",
                                  help="Enter the Z dimension in positive integers.", key="dimension_z")
    pixel_per_metric = st.number_input("Pixel per Metric", value=1.0, min_value=0.0, step=0.01, format="%.2f",
                                       help="Enter the pixel per metric value.", key="pixel_per_metric")
    link = st.text_input("Link", value="http://example.com/data",
                         help="Enter a URL for the file.", key="link")
    mask_exist = st.checkbox("Does Mask Exist?", value=True,
                             help="Check if a mask exists for the file.", key="mask_exist")
    mask_link = st.text_input("Mask Link", value="http://example.com/mask",
                              help="Enter a URL for the mask, if applicable.", key="mask_link")

    submit_experiment = st.form_submit_button("Create Experiment")


    if submit_experiment:
        if not external_experiment_id:
            st.error("Experiment ID is required!")
        else:
            organizational_data_dict = {
                "experiment_title": experiment_title,
                "external_experiment_id": external_experiment_id,
                "measurement_id": measurement_id,
                "upload_date": upload_date,
                "measurement_date": measurement_date,
                "institution": institution,
                "founding_body": founding_body,
                "country": country,
                "author": author,
                "orcid": orcid,
                "email": email,
                "published": published,
                "publication": publication,
                "doi": doi,
                "journal": journal,
                "volume": volume,
                "issue": issue,
                "pages": pages,
                "publication_date": publication_date,
                "topic": topic,
                "device": device,
                "component": component,
                "subcomponent": subcomponent,
                "granularity_level": granularity_level,
                "format": format_,
                "file_size": file_size,
                "file_size_unit": file_size_unit,
                "file_name": file_name,
                "dimension_x": dimension_x,
                "dimension_y": dimension_y,
                "dimension_z": dimension_z,
                "pixel_per_metric": pixel_per_metric,
                "link": link,
                "mask_exist": mask_exist,
                "mask_link": mask_link,
            }
            # Create and save the Experiment organizational data
            experiment = Experiment.objects.create()
            experiment.save()
            organizational_data = OrganizationalData.objects.create(**organizational_data_dict, experiment=experiment)
            experiment.organizational_data=organizational_data
            experiment.save()
            st.success(f"Experiment '{organizational_data.external_experiment_id}' created successfully!")
            st.session_state["experiment_id"] = experiment.experiment_id


def create_synthesis_and_steps(synthesis_data):
    experiment = Experiment.objects.filter(experiment_id=st.session_state["experiment_id"]).first()
    if not experiment:
        st.error("No experiment found. Please create the experiment first.")
        return

    synthesis, _ = Synthesis.objects.get_or_create(experiment=experiment)
    for i, step in enumerate(synthesis_data):
        print("SYNTHESIS STEP", i, step)
        technique = Technique.objects.create(
            name=step.get("technique_name", ""),
            description=step.get("technique_description", "")
        )

        synthesis_step = SynthesisStep.objects.create(technique=technique, order = i+1)
        for precursor in step.get("precursors", []):
            material = Material.objects.create(
                name=precursor["name"],
                amount=precursor["amount"],
                unit=precursor["unit"],
                lot_number=precursor["lot_number"]
            )
            synthesis_step.precursor_materials.add(material)

        for target in step.get("targets", []):
            material = Material.objects.create(
                name=target["name"],
                amount=target["amount"],
                unit=target["unit"],
                lot_number=target["lot_number"]
            )
            synthesis_step.target_materials.add(material)

        # Add synthesis_step to synthesis
        synthesis_step.save()
        synthesis.steps.add(synthesis_step)
    synthesis.save()
    experiment.synthesis = synthesis
    experiment.save()
    st.success(f"Synthesis with {len(synthesis_data)} steps added to Experiment '{st.session_state['experiment_id']}' successfully!")


def create_sample_preparation_and_steps(sp_data):
    experiment = Experiment.objects.filter(experiment_id=st.session_state["experiment_id"]).first()
    if not experiment:
        st.error("No experiment found. Please create the experiment first.")
        return

    sample_preparation, _ = SamplePreparation.objects.get_or_create(experiment=experiment)

    for step in sp_data:
        technique = Technique.objects.create(
            name=step.get("technique_name", ""),
            description=step.get("technique_description", "")
        )

        sp_step = SamplePreparationStep.objects.create(technique=technique)

        for precursor in step.get("precursors", []):
            material = Material.objects.create(
                name=precursor["name"],
                amount=precursor["amount"],
                unit=precursor["unit"],
                lot_number=precursor["lot_number"]
            )
            sp_step.precursor_materials.add(material)

        for target in step.get("targets", []):
            material = Material.objects.create(
                name=target["name"],
                amount=target["amount"],
                unit=target["unit"],
                lot_number=target["lot_number"]
            )
            sp_step.target_materials.add(material)

        sample_preparation.steps.add(sp_step)
    experiment.sample_preparation = sample_preparation
    experiment.save()
    st.success(f"Sample Preparation with {len(sp_data)} steps added to Experiment '{st.session_state['experiment_id']}' successfully!")


def create_sample_characterization():
    experiment = Experiment.objects.filter(experiment_id=st.session_state["experiment_id"]).first()
    if not experiment:
        st.info("Please create the Experiment first.")
        return

    with st.form(key="characterization_form"):
        st.subheader("Characterization / Measurement Data")
        measurement_method = st.text_input("Measurement Method", value="Default Method", key="ch_method")
        measurement_type = st.text_input("Measurement Type", value="Default Type", key="ch_type")
        specimen = st.text_input("Specimen", value="Default Specimen", key="ch_specimen")
        temperature = st.number_input("Temperature", value=25.0, step=0.1, key = "ch_temperature")
        temperature_unit = st.text_input("Temperature Unit", value="C", max_chars=10, key="ch_temp_unit")
        pressure = st.number_input("Pressure", value=1.0, step=0.1, key = "ch_pressure")
        pressure_unit = st.text_input("Pressure Unit", value="bar", max_chars=10, key="ch_pressure_unit")
        atmosphere = st.text_input("Atmosphere", value="Air", key="ch_atmosphere")

        submit_characterization = st.form_submit_button("Submit Characterization")
        if submit_characterization:
            characterization = Measurement.objects.create(
                experiment=experiment,
                measurement_method=measurement_method,
                measurement_type=measurement_type,
                specimen=specimen,
                temperature=temperature,
                temperature_unit=temperature_unit,
                pressure=pressure,
                pressure_unit=pressure_unit,
                atmosphere=atmosphere
            )
            experiment.characterization = characterization
            characterization.save()
            experiment.save()
            st.success("Characterization data has been recorded successfully!")


def ensure_step_data_structure():
    if "synthesis_steps_data" not in st.session_state:
        st.session_state.synthesis_steps_data = []
    if "sample_preparation_steps_data" not in st.session_state:
        st.session_state.sample_preparation_steps_data = []
    if "analysis_steps_data" not in st.session_state:
        st.session_state.analysis_steps_data = []


def add_synthesis_step():
    ensure_step_data_structure()
    st.session_state.synthesis_steps_data.append({
        "technique_name": "Default Technique",
        "technique_description": "Default Technique Description",
        "precursors": [],
        "targets": [],
        "metadata": [],
        "parameters": []
    })


def add_sp_step():
    ensure_step_data_structure()
    st.session_state.sample_preparation_steps_data.append({
        "technique_name": "Default Technique",
        "technique_description": "Default Technique Description",
        "precursors": [],
        "targets": [],
        "metadata": [],
        "parameters": []
    })


def add_precursor(step_index):
    st.session_state.synthesis_steps_data[step_index]["precursors"].append({
        "name": "Default Precursor",
        "amount": 1.0,
        "unit": "g",
        "lot_number": "LOT123"
    })


def add_target(step_index):
    st.session_state.synthesis_steps_data[step_index]["targets"].append({
        "name": "Default Target",
        "amount": 2.0,
        "unit": "mg",
        "lot_number": "TLOT123"
    })


def add_synthesis_metadata(step_index):
    st.session_state.synthesis_steps_data[step_index]["metadata"].append({
        "key": "default_key",
        "value": "default_value"
    })


def add_synthesis_parameter(step_index):
    st.session_state.synthesis_steps_data[step_index]["parameters"].append({
        "key": "default_parameter",
        "value": "default_value"
    })


def render_synthesis_step_form(step_index):
    step_data = st.session_state.synthesis_steps_data[step_index]
    step_data["technique_name"] = st.text_input(f"Technique Name (Synthesis Step {step_index+1})", value=step_data["technique_name"], key=f"s_technique_name_{step_index}")
    step_data["technique_description"] = st.text_area(f"Technique Description (Synthesis Step {step_index+1})", value=step_data["technique_description"], key=f"s_technique_description_{step_index}")

    st.markdown(f"**Precursor Materials (Synthesis Step {step_index+1})**")
    for i, precursor in enumerate(step_data["precursors"]):
        step_data["precursors"][i]["name"] = st.text_input(f"Precursor {i+1} Name", value=precursor["name"], key=f"s_precursor_name_{step_index}_{i}")
        step_data["precursors"][i]["amount"] = st.number_input(f"Precursor {i+1} Amount", value=precursor["amount"], step=0.1, key=f"s_precursor_amount_{step_index}_{i}")
        step_data["precursors"][i]["unit"] = st.text_input(f"Precursor {i+1} Unit", value=precursor["unit"], key=f"s_precursor_unit_{step_index}_{i}")
        step_data["precursors"][i]["lot_number"] = st.text_input(f"Precursor {i+1} Lot Number", value=precursor["lot_number"], key=f"s_precursor_lot_{step_index}_{i}")

    st.markdown(f"**Target Materials (Synthesis Step {step_index+1})**")
    for i, target in enumerate(step_data["targets"]):
        step_data["targets"][i]["name"] = st.text_input(f"Target {i+1} Name", value=target["name"], key=f"s_target_name_{step_index}_{i}")
        step_data["targets"][i]["amount"] = st.number_input(f"Target {i+1} Amount", value=target["amount"], step=0.1, key=f"s_target_amount_{step_index}_{i}")
        step_data["targets"][i]["unit"] = st.text_input(f"Target {i+1} Unit", value=target["unit"], key=f"s_target_unit_{step_index}_{i}")
        step_data["targets"][i]["lot_number"] = st.text_input(f"Target {i+1} Lot Number", value=target["lot_number"], key=f"s_target_lot_{step_index}_{i}")

    st.markdown(f"**Metadata (Synthesis Step {step_index+1})**")
    for i, md in enumerate(step_data["metadata"]):
        step_data["metadata"][i]["key"] = st.text_input(f"Metadata {i+1} Key", value=md["key"], key=f"s_metadata_key_{step_index}_{i}")
        step_data["metadata"][i]["value"] = st.text_input(f"Metadata {i+1} Value", value=md["value"], key=f"s_metadata_value_{step_index}_{i}")

    st.markdown(f"**Parameters (Synthesis Step {step_index+1})**")
    for i, param in enumerate(step_data["parameters"]):
        step_data["parameters"][i]["key"] = st.text_input(f"Parameter {i+1} Key", value=param["key"], key=f"s_parameter_key_{step_index}_{i}")
        step_data["parameters"][i]["value"] = st.text_input(f"Parameter {i+1} Value", value=param["value"], key=f"s_parameter_value_{step_index}_{i}")


# Sample Preparation functions
def add_sp_precursor(step_index):
    st.session_state.sample_preparation_steps_data[step_index]["precursors"].append({
        "name": "Default Precursor",
        "amount": 1.0,
        "unit": "g",
        "lot_number": "LOT123"
    })


def add_sp_target(step_index):
    st.session_state.sample_preparation_steps_data[step_index]["targets"].append({
        "name": "Default Target",
        "amount": 2.0,
        "unit": "mg",
        "lot_number": "TLOT123"
    })


def add_sp_metadata(step_index):
    st.session_state.sample_preparation_steps_data[step_index]["metadata"].append({
        "key": "default_key",
        "value": "default_value"
    })


def add_sp_parameter(step_index):
    st.session_state.sample_preparation_steps_data[step_index]["parameters"].append({
        "key": "default_parameter",
        "value": "default_value"
    })


def render_sample_preparation_step_form(step_index):
    step_data = st.session_state.sample_preparation_steps_data[step_index]
    step_data["technique_name"] = st.text_input(f"Technique Name (Sample Prep Step {step_index+1})", value=step_data["technique_name"], key=f"sp_technique_name_{step_index}")
    step_data["technique_description"] = st.text_area(f"Technique Description (Sample Prep Step {step_index+1})", value=step_data["technique_description"], key=f"sp_technique_description_{step_index}")

    st.markdown(f"**Precursor Materials (Sample Prep Step {step_index+1})**")
    for i, precursor in enumerate(step_data["precursors"]):
        step_data["precursors"][i]["name"] = st.text_input(f"Precursor {i+1} Name", value=precursor["name"], key=f"sp_precursor_name_{step_index}_{i}")
        step_data["precursors"][i]["amount"] = st.number_input(f"Precursor {i+1} Amount", value=precursor["amount"], step=0.1, key=f"sp_precursor_amount_{step_index}_{i}")
        step_data["precursors"][i]["unit"] = st.text_input(f"Precursor {i+1} Unit", value=precursor["unit"], key=f"sp_precursor_unit_{step_index}_{i}")
        step_data["precursors"][i]["lot_number"] = st.text_input(f"Precursor {i+1} Lot Number", value=precursor["lot_number"], key=f"sp_precursor_lot_{step_index}_{i}")

    st.markdown(f"**Target Materials (Sample Prep Step {step_index+1})**")
    for i, target in enumerate(step_data["targets"]):
        step_data["targets"][i]["name"] = st.text_input(f"Target {i+1} Name", value=target["name"], key=f"sp_target_name_{step_index}_{i}")
        step_data["targets"][i]["amount"] = st.number_input(f"Target {i+1} Amount", value=target["amount"], step=0.1, key=f"sp_target_amount_{step_index}_{i}")
        step_data["targets"][i]["unit"] = st.text_input(f"Target {i+1} Unit", value=target["unit"], key=f"sp_target_unit_{step_index}_{i}")
        step_data["targets"][i]["lot_number"] = st.text_input(f"Target {i+1} Lot Number", value=target["lot_number"], key=f"sp_target_lot_{step_index}_{i}")

    st.markdown(f"**Metadata (Sample Prep Step {step_index+1})**")
    for i, md in enumerate(step_data["metadata"]):
        step_data["metadata"][i]["key"] = st.text_input(f"Metadata {i+1} Key", value=md["key"], key=f"sp_metadata_key_{step_index}_{i}")
        step_data["metadata"][i]["value"] = st.text_input(f"Metadata {i+1} Value", value=md["value"], key=f"sp_metadata_value_{step_index}_{i}")

    st.markdown(f"**Parameters (Sample Prep Step {step_index+1})**")
    for i, param in enumerate(step_data["parameters"]):
        step_data["parameters"][i]["key"] = st.text_input(f"Parameter {i+1} Key", value=param["key"], key=f"sp_parameter_key_{step_index}_{i}")
        step_data["parameters"][i]["value"] = st.text_input(f"Parameter {i+1} Value", value=param["value"], key=f"sp_parameter_value_{step_index}_{i}")


# Analysis functions
def add_analysis_step():
    ensure_step_data_structure()
    st.session_state.analysis_steps_data.append({
        "technique_name": "Default Technique",
        "technique_description": "Default Technique Description",
        "input_items": [],     # representing Union[Data, Quantity]
        "metadata": [],
        "parameters": [],
        "results": "Default results"
    })


def add_analysis_input(step_index):
    print("Adding input to analysis step", step_index)
    st.session_state.analysis_steps_data[step_index]["input_items"].append({
        "name": "Default Input",
        "type": "Data"  # or "Quantity"
    })


def add_analysis_metadata(step_index):
    st.session_state.analysis_steps_data[step_index]["metadata"].append({
        "key": "default_key",
        "value": "default_value"
    })


def add_analysis_parameter(step_index):
    st.session_state.analysis_steps_data[step_index]["parameters"].append({
        "key": "default_parameter",
        "value": "default_value"
    })


def ensure_step_data_structure():
    if "synthesis_steps_data" not in st.session_state:
        st.session_state.synthesis_steps_data = []
    if "sample_preparation_steps_data" not in st.session_state:
        st.session_state.sample_preparation_steps_data = []
    if "analysis_steps_data" not in st.session_state:
        st.session_state.analysis_steps_data = []


def add_analysis_step():
    ensure_step_data_structure()
    print("Adding analysis step", len(st.session_state.analysis_steps_data))
    st.session_state.analysis_steps_data.append({
        "technique": "Default Technique",
        "data_inputs": [],       # list of data input dicts
        "quantity_inputs": [],   # list of quantity input dicts
        "metadata": [],          # list of metadata dicts
        "parameters": [],        # list of parameter dicts
        "data_results": [],      # list of data output dicts
        "quantity_results": [],  # list of quantity output dicts
        "results": "Default results"
    })


def add_data_input(step_index):
    print("Adding data input to analysis step", step_index)
    print(st.session_state.analysis_steps_data)
    st.session_state.analysis_steps_data[step_index]["data_inputs"].append({
        "data_type": "default_type",
        "data_format": "default_format"
    })


def add_quantity_input(step_index):
    st.session_state.analysis_steps_data[step_index]["quantity_inputs"].append({
        "value": 0.0,
        "error": 0.0,
        "unit": "unit"
    })


def add_metadata(step_index):
    st.session_state.analysis_steps_data[step_index]["metadata"].append({
        "key": "default_key",
        "value": "default_value"
    })


def add_parameter(step_index):
    st.session_state.analysis_steps_data[step_index]["parameters"].append({
        "key": "default_parameter",
        "value": "default_value"
    })


def add_data_output(step_index):
    st.session_state.analysis_steps_data[step_index]["data_results"].append({
        "data_type": "default_type",
        "data_format": "default_format"
    })


def add_quantity_output(step_index):
    st.session_state.analysis_steps_data[step_index]["quantity_results"].append({
        "value": 0.0,
        "error": 0.0,
        "unit": "unit"
    })


def render_data_item_form(item, label_prefix):
    item["data_type"] = st.text_input(f"{label_prefix} Data Type", value=item["data_type"], key = str(uuid.uuid4()))
    item["data_format"] = st.text_input(f"{label_prefix} Data Format", value=item["data_format"], key = str(uuid.uuid4()))
    file_or_link = st.radio(f"{label_prefix} Source", ["File Upload", "Link"], index=0 if "file_data" in item else 1, key = str(uuid.uuid4()))
    if file_or_link == "File Upload":
        uploaded_file = st.file_uploader(f"Upload {label_prefix} Data File")
        if uploaded_file is not None:
            item["file_data"] = uploaded_file
        if "link" in item:
            del item["link"]
    else:
        link_val = item.get("link", "")
        item["link"] = st.text_input(f"{label_prefix} Link", value=link_val, key = str(uuid.uuid4()))
        if "file_data" in item:
            del item["file_data"]


def render_quantity_item_form(item, label_prefix):
    item["value"] = st.number_input(f"{label_prefix} Value", value=item.get("value", 0.0), step=0.1, key = str(uuid.uuid4()))
    item["error"] = st.number_input(f"{label_prefix} Error", value=item.get("error", 0.0), step=0.1, key = str(uuid.uuid4()))
    item["unit"] = st.text_input(f"{label_prefix} Unit", value=item.get("unit", "unit"), key = str(uuid.uuid4()))


def render_analysis_step_form(step_index):
    step_data = st.session_state.analysis_steps_data[step_index]
    step_data["technique"] = st.text_area(f"Technique (Analysis Step {step_index+1})", value=step_data["technique"], key= str(uuid.uuid4()))

    # Data Inputs
    st.markdown(f"**Data Inputs (Analysis Step {step_index+1})**")
    for i, d_inp in enumerate(step_data["data_inputs"]):
        st.markdown(f"**Data Input {i+1}:**")
        render_data_item_form(d_inp, f"Data Input {i+1}")

    # Quantity Inputs
    st.markdown(f"**Quantity Inputs (Analysis Step {step_index+1})**")
    for i, q_inp in enumerate(step_data["quantity_inputs"]):
        st.markdown(f"**Quantity Input {i+1}:**")
        render_quantity_item_form(q_inp, f"Quantity Input {i+1}")

    # Metadata
    st.markdown(f"**Metadata (Analysis Step {step_index+1})**")
    for i, md in enumerate(step_data["metadata"]):
        step_data["metadata"][i]["key"] = st.text_input(f"Metadata {i+1} Key", value=md["key"], key= str(uuid.uuid4()))
        step_data["metadata"][i]["value"] = st.text_input(f"Metadata {i+1} Value", value=md["value"], key= str(uuid.uuid4()))

    # Parameters
    st.markdown(f"**Parameters (Analysis Step {step_index+1})**")
    for i, param in enumerate(step_data["parameters"]):
        step_data["parameters"][i]["key"] = st.text_input(f"Parameter {i+1} Key", value=param["key"], key= str(uuid.uuid4()))
        step_data["parameters"][i]["value"] = st.text_input(f"Parameter {i+1} Value", value=param["value"], key= str(uuid.uuid4()))

    # Data Outputs
    st.markdown(f"**Data Outputs (Analysis Step {step_index+1})**")
    for i, d_out in enumerate(step_data["data_results"]):
        st.markdown(f"**Data Output {i+1}:**")
        render_data_item_form(d_out, f"Data Output {i+1}")

    # Quantity Outputs
    st.markdown(f"**Quantity Outputs (Analysis Step {step_index+1})**")
    for i, q_out in enumerate(step_data["quantity_results"]):
        st.markdown(f"**Quantity Output {i+1}:**")
        render_quantity_item_form(q_out, f"Quantity Output {i+1}")

    # Results
    step_data["results"] = st.text_area(f"Results (Analysis Step {step_index+1})", value=step_data["results"])


def create_analysis_and_steps(analysis_data):
    experiment = Experiment.objects.filter(experiment_id=st.session_state.get("experiment_id")).first()
    if not experiment:
        st.error("No experiment found. Please create the experiment first.")
        return
    print("ANALYSIS DATA IS ADDED HERE")

    analysis, _ = Analysis.objects.get_or_create()

    from django.core.files.base import ContentFile

    for i, step in enumerate(analysis_data):
        analysis_step = AnalysisStep.objects.create(
            technique=step.get("technique", ""),
            order = i
        )

        # Add Metadata
        for md in step.get("metadata", []):
            metadata_obj = Metadata.objects.create(key=md["key"], value=md["value"])
            analysis_step.metadata.add(metadata_obj)

        # Handle data_inputs
        for d_inp in step.get("data_inputs", []):
            data_kwargs = {
                "data_type": d_inp["data_type"],
                "data_format": d_inp["data_format"]
            }
            if "file_data" in d_inp and d_inp["file_data"] is not None:
                uploaded_file = d_inp["file_data"]
                content = uploaded_file.read()
                file_name = uploaded_file.name
                data_kwargs["data"] = ContentFile(content, name=file_name)
            elif "link" in d_inp and d_inp["link"]:
                data_kwargs["link"] = d_inp["link"]
            data_obj = Data.objects.create(**data_kwargs)
            analysis_step.data_inputs.add(data_obj)

        # Handle quantity_inputs
        for q_inp in step.get("quantity_inputs", []):
            qty = Quantity.objects.create(
                value=q_inp["value"],
                error=q_inp["error"],
                unit=q_inp["unit"]
            )
            analysis_step.quantity_inputs.add(qty)

        # Handle data_results
        for d_out in step.get("data_results", []):
            data_kwargs = {
                "data_type": d_out["data_type"],
                "data_format": d_out["data_format"]
            }
            if "file_data" in d_out and d_out["file_data"] is not None:
                uploaded_file = d_out["file_data"]
                content = uploaded_file.read()
                file_name = uploaded_file.name
                data_kwargs["data"] = ContentFile(content, name=file_name)
            elif "link" in d_out and d_out["link"]:
                data_kwargs["link"] = d_out["link"]
            data_obj = Data.objects.create(**data_kwargs)
            analysis_step.data_results.add(data_obj)

        # Handle quantity_results
        for q_out in step.get("quantity_results", []):
            qty = Quantity.objects.create(
                value=q_out["value"],
                error=q_out["error"],
                unit=q_out["unit"]
            )
            analysis_step.quantity_results.add(qty)

        analysis.steps.add(analysis_step)
    experiment.analysis = analysis
    experiment.save()
    st.success(f"Analysis with {len(analysis_data)} steps added successfully!")


# Preprocessing-related functions
def ensure_preprocessing_data_structure():
    if "preprocessing_steps_data" not in st.session_state:
        st.session_state.preprocessing_steps_data = []

def add_preprocessing_step():
    ensure_preprocessing_data_structure()
    st.session_state.preprocessing_steps_data.append({
        "technique": "Default Technique",
        "data_inputs": [],
        "quantity_inputs": [],
        "metadata": [],
        "parameters": [],
        "data_results": [],
        "quantity_results": [],
        "results": "Default results"
    })

def add_preprocessing_data_input(step_index):
    st.session_state.preprocessing_steps_data[step_index]["data_inputs"].append({
        "data_type": "default_type",
        "data_format": "default_format"
    })

def add_preprocessing_quantity_input(step_index):
    st.session_state.preprocessing_steps_data[step_index]["quantity_inputs"].append({
        "value": 0.0,
        "error": 0.0,
        "unit": "unit"
    })

def add_preprocessing_metadata(step_index):
    st.session_state.preprocessing_steps_data[step_index]["metadata"].append({
        "key": "default_key",
        "value": "default_value"
    })

def add_preprocessing_parameter(step_index):
    st.session_state.preprocessing_steps_data[step_index]["parameters"].append({
        "key": "default_parameter",
        "value": "default_value"
    })

def add_preprocessing_data_output(step_index):
    st.session_state.preprocessing_steps_data[step_index]["data_results"].append({
        "data_type": "default_type",
        "data_format": "default_format"
    })

def add_preprocessing_quantity_output(step_index):
    st.session_state.preprocessing_steps_data[step_index]["quantity_results"].append({
        "value": 0.0,
        "error": 0.0,
        "unit": "unit"
    })

def render_preprocessing_data_item_form(item, label_prefix):
    item["data_type"] = st.text_input(f"{label_prefix} Data Type", value=item["data_type"], key = str(uuid.uuid4()))
    item["data_format"] = st.text_input(f"{label_prefix} Data Format", value=item["data_format"], key=str(uuid.uuid4()))
    file_or_link = st.radio(f"{label_prefix} Source", ["File Upload", "Link"], index=0 if "file_data" in item else 1, key=str(uuid.uuid4()))
    if file_or_link == "File Upload":
        uploaded_file = st.file_uploader(f"Upload {label_prefix} Data File")
        if uploaded_file is not None:
            item["file_data"] = uploaded_file
        if "link" in item:
            del item["link"]
    else:
        link_val = item.get("link", "")
        item["link"] = st.text_input(f"{label_prefix} Link", value=link_val, key= str(uuid.uuid4()))
        if "file_data" in item:
            del item["file_data"]

def render_preprocessing_quantity_item_form(item, label_prefix):
    item["value"] = st.number_input(f"{label_prefix} Value", value=item.get("value", 0.0), step=0.1, key=str(uuid.uuid4()))
    item["error"] = st.number_input(f"{label_prefix} Error", value=item.get("error", 0.0), step=0.1, key=str(uuid.uuid4()))
    item["unit"] = st.text_input(f"{label_prefix} Unit", value=item.get("unit", "unit"), key = str(uuid.uuid4()))
    item["name"] = st.text_input(f"{label_prefix} Name", value=item.get("name", "name"), key = str(uuid.uuid4()))

def render_preprocessing_step_form(step_index):
    step_data = st.session_state.preprocessing_steps_data[step_index]
    step_data["technique"] = st.text_area(f"Technique (Preprocessing Step {step_index+1})", value=step_data["technique"], key=f"preprocess_technique_{step_index}")

    # Data Inputs
    st.markdown(f"**Data Inputs (Preprocessing Step {step_index+1})**")
    for i, d_inp in enumerate(step_data["data_inputs"]):
        st.markdown(f"**Data Input {i+1}:**")
        render_preprocessing_data_item_form(d_inp, f"Data Input {i+1}")

    # Quantity Inputs
    st.markdown(f"**Quantity Inputs (Preprocessing Step {step_index+1})**")
    for i, q_inp in enumerate(step_data["quantity_inputs"]):
        st.markdown(f"**Quantity Input {i+1}:**")
        render_preprocessing_quantity_item_form(q_inp, f"Quantity Input {i+1}")

    # Metadata
    st.markdown(f"**Metadata (Preprocessing Step {step_index+1})**")
    for i, md in enumerate(step_data["metadata"]):
        step_data["metadata"][i]["key"] = st.text_input(f"Metadata {i+1} Key", value=md["key"], key=f"preprocess_metadata_key_{step_index}_{i}")
        step_data["metadata"][i]["value"] = st.text_input(f"Metadata {i+1} Value", value=md["value"], key=f"preprocess_metadata_value_{step_index}_{i}")

    # Parameters
    st.markdown(f"**Parameters (Preprocessing Step {step_index+1})**")
    for i, param in enumerate(step_data["parameters"]):
        step_data["parameters"][i]["name"] = st.text_input(f"Parameter {i+1} Key", value=param["key"], key=f"preprocess_parameter_key_{step_index}_{i}")
        step_data["parameters"][i]["value"] = st.text_input(f"Parameter {i+1} Value", value=param["value"], key=f"preprocess_parameter_value_{step_index}_{i}")
        step_data["parameters"][i]["unit"] = st.text_input(f"Parameter {i+1} Value", value=param["value"], key=f"preprocess_parameter_unit_{step_index}_{i}")
        step_data["parameters"][i]["error"] = st.text_input(f"Parameter {i+1} Value", value=param["value"], key=f"preprocess_parameter_error_{step_index}_{i}")

    # Data Outputs
    st.markdown(f"**Data Outputs (Preprocessing Step {step_index+1})**")
    for i, d_out in enumerate(step_data["data_results"]):
        st.markdown(f"**Data Output {i+1}:**")
        render_preprocessing_data_item_form(d_out, f"Data Output {i+1}")

    # Quantity Outputs
    st.markdown(f"**Quantity Outputs (Preprocessing Step {step_index+1})**")
    for i, q_out in enumerate(step_data["quantity_results"]):
        st.markdown(f"**Quantity Output {i+1}:**")
        render_preprocessing_quantity_item_form(q_out, f"Quantity Output {i+1}")

    # Results
    step_data["results"] = st.text_area(f"Results (Preprocessing Step {step_index+1})", value=step_data["results"])

def create_preprocessing_and_steps(preprocessing_data):
    experiment = Experiment.objects.filter(experiment_id=st.session_state.get("experiment_id")).first()
    if not experiment:
        st.error("No experiment found. Please create the experiment first.")
        return

    # We assume Preprocessing and PreprocessingStep have the same structure as Analysis and AnalysisStep
    # and are imported models.
    preprocessing, _ = Preprocessing.objects.get_or_create(
        experiment=experiment
    )

    from django.core.files.base import ContentFile

    for i, step in enumerate(preprocessing_data):
        preprocessing_step = PreprocessingStep.objects.create(
            technique=step.get("technique", ""),
            order = i
        )

        # Add Metadata
        for md in step.get("metadata", []):
            metadata_obj = Metadata.objects.create(key=md["key"], value=md["value"])
            preprocessing_step.metadata.add(metadata_obj)

        # data_inputs
        for d_inp in step.get("data_inputs", []):
            data_kwargs = {
                "data_type": d_inp["data_type"],
                "data_format": d_inp["data_format"]
            }
            if "file_data" in d_inp and d_inp["file_data"] is not None:
                uploaded_file = d_inp["file_data"]
                content = uploaded_file.read()
                file_name = uploaded_file.name
                data_kwargs["data"] = ContentFile(content, name=file_name)
            elif "link" in d_inp and d_inp["link"]:
                data_kwargs["link"] = d_inp["link"]
            data_obj = Data.objects.create(**data_kwargs)
            preprocessing_step.data_inputs.add(data_obj)

        # quantity_inputs
        for q_inp in step.get("quantity_inputs", []):
            qty = Quantity.objects.create(
                value=q_inp["value"],
                error=q_inp["error"],
                unit=q_inp["unit"],
                name=q_inp["name"]
            )
            preprocessing_step.quantity_inputs.add(qty)

        # data_results
        for d_out in step.get("data_results", []):
            data_kwargs = {
                "data_type": d_out["data_type"],
                "data_format": d_out["data_format"]
            }
            if "file_data" in d_out and d_out["file_data"] is not None:
                uploaded_file = d_out["file_data"]
                content = uploaded_file.read()
                file_name = uploaded_file.name
                data_kwargs["data"] = ContentFile(content, name=file_name)
            elif "link" in d_out and d_out["link"]:
                data_kwargs["link"] = d_out["link"]
            data_obj = Data.objects.create(**data_kwargs)
            preprocessing_step.data_results.add(data_obj)

        # quantity_results
        for q_out in step.get("quantity_results", []):
            qty = Quantity.objects.create(
                value=q_out["value"],
                error=q_out["error"],
                unit=q_out["unit"],
                name=q_out["name"]
            )
            preprocessing_step.quantity_results.add(qty)

        preprocessing.steps.add(preprocessing_step)
    preprocessing.save()
    experiment.preprocessing = preprocessing
    experiment.save()

    st.success(f"Preprocessing with {len(preprocessing_data)} steps added successfully!")



# Streamlit App
menu = ["Add Experiment", "View Experiments", "Search Experiments"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Experiment":
    st.header("Add New Experiment")

    # Use tabs: Organizational Data, Measurement, Synthesis Steps, Sample Preparation, Analysis
    tabs = st.tabs(["Organizational Data", "Measurement", "Synthesis Steps", "Sample Preparation", "Data Preprocessing", "Analysis"])

    with tabs[0]:
        with st.form(key="organizational_data_form"):
            define_organizational_data_form()

    with tabs[1]:
        if "experiment_id" not in st.session_state:
            st.info("Please create the Experiment first in the 'Organizational Data' tab.")
        else:
            create_sample_characterization()

    with tabs[2]:
        if "experiment_id" not in st.session_state:
            st.info("Please create the Experiment first in the 'Organizational Data' tab.")
        else:
            st.subheader("Define Synthesis Steps for the Experiment")
            ensure_step_data_structure()

            if st.button("Add Synthesis Step"):
                add_synthesis_step()

            for i, step_data in enumerate(st.session_state.synthesis_steps_data):
                st.markdown(f"---\n### Manage Synthesis Step {i+1} Components")
                cols = st.columns(4)
                with cols[0]:
                    if st.button(f"Add Precursor (Synthesis Step {i+1})"):
                        add_precursor(i)
                with cols[1]:
                    if st.button(f"Add Target (Synthesis Step {i+1})"):
                        add_target(i)
                with cols[2]:
                    if st.button(f"Add Metadata (Synthesis Step {i+1})"):
                        add_synthesis_metadata(i)
                with cols[3]:
                    if st.button(f"Add Parameter (Synthesis Step {i+1})"):
                        add_synthesis_parameter(i)

            with st.form(key="synthesis_steps_form"):
                for i in range(len(st.session_state.synthesis_steps_data)):
                    render_synthesis_step_form(i)

                submit_synthesis = st.form_submit_button("Submit Synthesis Steps")
                if submit_synthesis:
                    create_synthesis_and_steps(st.session_state.synthesis_steps_data)

    with tabs[3]:
        if "experiment_id" not in st.session_state:
            st.info("Please create the Experiment first in the 'Organizational Data' tab.")
        else:
            st.subheader("Define Sample Preparation Steps for the Experiment")
            ensure_step_data_structure()

            if st.button("Add Sample Preparation Step"):
                add_sp_step()

            for i, step_data in enumerate(st.session_state.sample_preparation_steps_data):
                st.markdown(f"---\n### Manage Sample Preparation Step {i+1} Components")
                sp_cols = st.columns(4)
                with sp_cols[0]:
                    if st.button(f"Add Precursor (Sample Prep Step {i+1})"):
                        add_sp_precursor(i)
                with sp_cols[1]:
                    if st.button(f"Add Target (Sample Prep Step {i+1})"):
                        add_sp_target(i)
                with sp_cols[2]:
                    if st.button(f"Add Metadata (Sample Prep Step {i+1})"):
                        add_sp_metadata(i)
                with sp_cols[3]:
                    if st.button(f"Add Parameter (Sample Prep Step {i+1})"):
                        add_sp_parameter(i)

            with st.form(key="sample_preparation_form"):
                for i in range(len(st.session_state.sample_preparation_steps_data)):
                    render_sample_preparation_step_form(i)

                submit_sp = st.form_submit_button("Submit Sample Preparation Steps")
                if submit_sp:
                    create_sample_preparation_and_steps(st.session_state.sample_preparation_steps_data)
    with tabs[4]:
        if "experiment_id" not in st.session_state:
            st.info("Please create the Experiment first in the 'Organizational Data' tab.")
        else:
            st.subheader("Define Data Preprocessing Steps for the Experiment")
            ensure_preprocessing_data_structure()

            if st.button("Add Preprocessing Step"):
                add_preprocessing_step()

            # For each Preprocessing step, add components (outside form)
            for i, step_data in enumerate(st.session_state.preprocessing_steps_data):
                st.markdown(f"---\n### Manage Preprocessing Step {i+1} Components")

                # First row of buttons
                p_row1 = st.columns(3)
                with p_row1[0]:
                    if st.button(f"Add Data Input (Preproc Step {i+1})"):
                        add_preprocessing_data_input(i)
                with p_row1[1]:
                    if st.button(f"Add Quantity Input (Preproc Step {i+1})"):
                        add_preprocessing_quantity_input(i)
                with p_row1[2]:
                    if st.button(f"Add Metadata (Preproc Step {i+1})"):
                        add_preprocessing_metadata(i)

                # Second row of buttons
                p_row2 = st.columns(3)
                with p_row2[0]:
                    if st.button(f"Add Parameter (Preproc Step {i+1})"):
                        add_preprocessing_parameter(i)
                with p_row2[1]:
                    if st.button(f"Add Data Output (Preproc Step {i+1})"):
                        add_preprocessing_data_output(i)
                with p_row2[2]:
                    if st.button(f"Add Quantity Output (Preproc Step {i+1})"):
                        add_preprocessing_quantity_output(i)

            with st.form(key="preprocessing_form"):
                for i in range(len(st.session_state.preprocessing_steps_data)):
                    render_preprocessing_step_form(i)

                submit_preprocessing = st.form_submit_button("Submit Preprocessing Steps")
                if submit_preprocessing:
                    create_preprocessing_and_steps(st.session_state.preprocessing_steps_data)
    with tabs[5]:
        if "experiment_id" not in st.session_state:
            st.info("Please create the Experiment first in the 'Organizational Data' tab.")
        else:
            st.subheader("Define Analysis Steps for the Experiment")
            ensure_step_data_structure()

            if st.button("Add Analysis Step"):
                add_analysis_step()

            # For each Analysis step, add components (outside form)
            for i, step_data in enumerate(st.session_state.analysis_steps_data):
                st.markdown(f"---\n### Manage Analysis Step {i+1} Components")

                # First row of buttons: add data input, add quantity input, add metadata
                row1 = st.columns(3)
                with row1[0]:
                    if st.button(f"Add Data Input (Step {i+1})"):
                        add_data_input(i)
                with row1[1]:
                    if st.button(f"Add Quantity Input (Step {i+1})"):
                        add_quantity_input(i)
                with row1[2]:
                    if st.button(f"Add Metadata (Step {i+1})"):
                        add_metadata(i)

                # Second row of buttons: add parameter, add data output, add quantity output
                row2 = st.columns(3)
                with row2[0]:
                    if st.button(f"Add Parameter (Step {i+1})"):
                        add_parameter(i)
                with row2[1]:
                    if st.button(f"Add Data Output (Step {i+1})"):
                        add_data_output(i)
                with row2[2]:
                    if st.button(f"Add Quantity Output (Step {i+1})"):
                        add_quantity_output(i)

            with st.form(key="analysis_form"):
                for i in range(len(st.session_state.analysis_steps_data)):
                    render_analysis_step_form(i)

                submit_analysis = st.form_submit_button("Submit Analysis Steps")
                if submit_analysis:
                    create_analysis_and_steps(st.session_state.analysis_steps_data)
elif choice == "View Experiments":
    st.header("View All Experiments")
    experiments = Experiment.objects.all()

    if experiments:
        for experiment in experiments:
            print(experiment)
            print("organizational_data", experiment.organizational_data)
            print("characterization", experiment.characterization)
            print("synthesis", experiment.synthesis)
            print("sample_preparation", experiment.sample_preparation)
            print("analysis", experiment.analysis)

            st.subheader(f"Experiment ID: {experiment.experiment_id}")
            if experiment.organizational_data:
                st.write("Name:", experiment.organizational_data.experiment_title)
                st.write("Description:", experiment.organizational_data.experiment_id)

            # Display Characterization Data
            if experiment.characterization is not None:
                    st.write("Characterizations:")
                    for char in experiment.characterization:
                        st.write(" - Measurement Method:", char.measurement_method)
                        st.write("   Measurement Type:", char.measurement_type)
                        st.write("   Specimen:", char.specimen)
                        st.write("   Temperature:", char.temperature, char.temperature_unit)
                        st.write("   Pressure:", char.pressure, char.pressure_unit)
                        st.write("   Atmosphere:", char.atmosphere)

            # Display Synthesis Steps
            st.write("Synthesis Steps:")
            print(experiment)
            print(experiment.synthesis)
            if experiment.synthesis is not None:
                for synthesis in experiment.synthesis.all():
                    for step in synthesis.steps.all():
                        st.write(f"  - Technique: {step.technique.name}")
                        st.write("    Description:", step.technique.description)
                        st.write("    Precursor Materials:")
                        for material in step.precursor_materials.all():
                            st.write(f"      - {material.name}, {material.amount} {material.unit} (Lot: {material.lot_number})")
                        st.write("    Target Materials:")
                        for material in step.target_materials.all():
                            st.write(f"      - {material.name}, {material.amount} {material.unit} (Lot: {material.lot_number})")

            # Display Sample Preparation Steps
            st.write("Sample Preparation Steps:")
            if experiment.sample_preparation is not None:
                for sp in experiment.sample_preparation.all():
                    for step in sp.steps.all():
                        st.write(f"  - Technique: {step.technique.name}")
                        st.write("    Description:", step.technique.description)
                        st.write("    Precursor Materials:")
                        for material in step.precursor_materials.all():
                            st.write(f"      - {material.name}, {material.amount} {material.unit} (Lot: {material.lot_number})")
                        st.write("    Target Materials:")
                        for material in step.target_materials.all():
                            st.write(f"      - {material.name}, {material.amount} {material.unit} (Lot: {material.lot_number})")

            # Display Analysis Steps
            st.write("Analysis Steps:")
            # If Analysis is not linked directly to Experiment, adjust as needed.
            if experiment.analysis is not None:
                for step in experiment.analysis.steps.all():
                    st.write(f"  Step {step.order + 1}:")
                    st.write(f"**Technique:** {step.technique}" if step.technique else "**Technique:** Not specified")

                    # Parameters
                    if step.parameter:
                        st.write("**Parameters:**")
                        for param in step.parameter.all():
                            for key, value in param.dict().items():
                                st.write(f" - {key}: {value}")
                    else:
                        st.write("**Parameters:** None")

                    # Data inputs
                    if step.data_inputs.exists():
                        st.write("**Data Inputs:**")
                        for data_input in step.data_inputs.all():
                            st.write(f" - Data Type: {data_input.data_type}, Format: {data_input.data_format}, Link: {data_input.link or 'N/A'}")
                    else:
                        st.write("**Data Inputs:** None")

                    # Quantity inputs
                    if step.quantity_inputs.exists():
                        st.write("**Quantity Inputs:**")
                        for qty_input in step.quantity_inputs.all():
                            st.write(f" - Value: {qty_input.value}, Error: {qty_input.error}, Unit: {qty_input.unit}")
                    else:
                        st.write("**Quantity Inputs:** None")

                    # Data results
                    if step.data_results.exists():
                        st.write("**Data Results:**")
                        for data_result in step.data_results.all():
                            st.write(f" - Data Type: {data_result.data_type}, Format: {data_result.data_format}, Link: {data_result.link or 'N/A'}")
                    else:
                        st.write("**Data Results:** None")

                    # Quantity results
                    if step.quantity_results.exists():
                        st.write("**Quantity Results:**")
                        for qty_result in step.quantity_results.all():
                            st.write(f" - Value: {qty_result.value}, Error: {qty_result.error}, Unit: {qty_result.unit}")
                    else:
                        st.write("**Quantity Results:** None")

                    # Metadata
                    if step.metadata is not None:
                        st.write("**Metadata:**")
                        for md in step.metadata.all():
                            st.write(f" - {md.key}: {md.value}")
                    else:
                        st.write("**Metadata:** None")

                st.write("---")  # Add a separator for readability
                st.write(f"   * {md.key}: {md.value}")
                    # If input items were represented as metadata placeholders, they're shown above as well.

    else:
        st.info("No experiments available.")
elif choice == "Search Experiments":
    st.header("Search for an Experiment by Different IDs")
    tab_ids, tab_advanced = st.tabs(["Search by ID", "Advanced Search"])
    with tab_ids:
        # 1) Provide a dropdown to choose which ID type we want to search
        search_option = st.selectbox(
            "Search By:",
            ["Experiment ID", "Measurement ID", "Synthesis ID", "Analysis ID", "Preprocessing ID"]
        )

        # 2) Based on the user’s choice, ask for the relevant ID value
        search_value = st.text_input(f"Enter the {search_option} to search for:")

        # 3) User chooses output format for retrieval
        output_format = st.selectbox("Choose output format", ["json", "csv"])

        # 4) Clicking this button triggers the search
        if st.button("Search"):
            if not search_value.strip():
                st.warning(f"Please provide a valid {search_option}.")
            else:
                # Attempt to find the Experiment based on user choice
                experiment = None

                if search_option == "Experiment ID":
                    experiment = Experiment.objects.filter(experiment_id=search_value).first()

                elif search_option == "Measurement ID":
                    measurement = Measurement.objects.filter(uid=search_value).first()
                    if measurement:
                        experiment = measurement.experiment  # Adjust if your FK is named differently

                elif search_option == "Synthesis ID":
                    synthesis = Synthesis.objects.filter(uid=search_value).first()
                    if synthesis:
                        experiment = synthesis.experiment

                elif search_option == "Analysis ID":
                    analysis = Analysis.objects.filter(uid=search_value).first()
                    if analysis:
                        # If you store experiment on the analysis object
                        # or if it's a ManyToMany, adjust as needed
                        experiment = analysis.experiment

                elif search_option == "Preprocessing ID":
                    preprocessing = Preprocessing.objects.filter(uid=search_value).first()
                    if preprocessing:
                        experiment = preprocessing.experiment

                # 5) Now that we (hopefully) have an Experiment, we can retrieve from Neo4j
                if experiment:
                    # If your Neo4j uses experiment.uid as the unique identifier,
                    # pass that to the retrieval handler:
                    experiment_uid = str(experiment.uid)  # or however you store it in the model

                    # Instantiate your retrieval handler
                    retrieval_handler = Neo4jDataRetrievalHandler()

                    # JSON
                    if output_format == "json":
                        try:
                            result_str = retrieval_handler.get_experiment_data(
                                experiment_uid=experiment_uid,
                                output_format='json'
                            )
                            # Provide a download button for JSON
                            st.download_button(
                                label=f"Download {search_value} as JSON",
                                data=result_str,
                                file_name=f"experiment_{search_value}.json",
                                mime="application/json"
                            )

                            # Optionally display JSON content:
                            st.json(result_str)

                        except Exception as e:
                            st.error(f"Error retrieving JSON data: {e}")

                    # CSV
                    else:
                        try:
                            with tempfile.TemporaryDirectory() as tmpdir:
                                # The handler’s CSV mode writes multiple CSVs into `tmpdir`
                                result_files = retrieval_handler.get_experiment_data(
                                    experiment_uid=experiment_uid,
                                    output_format='csv',
                                    base_path=tmpdir
                                )
                                # `result_files` is presumably a dict: { "experiment": /path/to/file, ... }

                                # Zip them up
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip_file:
                                    with zipfile.ZipFile(tmp_zip_file.name, 'w') as zipf:
                                        for label, filepath in result_files.items():
                                            arcname = os.path.basename(filepath)
                                            zipf.write(filepath, arcname=arcname)

                                    # Read ZIP content into memory
                                    zip_bytes = tmp_zip_file.read()

                                # Create a base64-encoded download link
                                b64_zip = base64.b64encode(zip_bytes).decode()
                                href = (
                                    f'<a href="data:application/zip;base64,{b64_zip}" '
                                    f'download="experiment_{search_value}.zip">Download CSV ZIP</a>'
                                )
                                st.markdown(href, unsafe_allow_html=True)

                        except Exception as e:
                            st.error(f"Error retrieving CSV data: {e}")

                else:
                    st.warning(f"No experiment found for {search_option}: {search_value}")
    with tab_advanced:
        advanced_search_tab_ui()