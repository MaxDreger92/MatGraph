import os
import django

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mat2devplatform.settings')
django.setup()

import pandas as pd
from dotenv import load_dotenv
from graphutils.embeddings import request_embedding
from importing.models import NodeLabel, NodeLabelEmbedding, MatterAttribute, MatterAttributeEmbedding, \
    MeasurementAttribute, MeasurementAttributeEmbedding, ManufacturingAttribute, ManufacturingAttributeEmbedding, \
    PropertyAttribute, PropertyAttributeEmbedding, ParameterAttribute, ParameterAttributeEmbedding, MetadataAttribute, \
    MetadataAttributeEmbedding

# Mapping of the class names to actual class objects
class_mapping = {
    'NodeLabel': NodeLabel,
    'NodeLabelEmbedding': NodeLabelEmbedding,
    'MatterAttribute': MatterAttribute,
    'MatterAttributeEmbedding': MatterAttributeEmbedding,
    'MeasurementAttribute': MeasurementAttribute,
    'MeasurementAttributeEmbedding': MeasurementAttributeEmbedding,
    'ManufacturingAttribute': ManufacturingAttribute,
    'ManufacturingAttributeEmbedding': ManufacturingAttributeEmbedding,
    'PropertyAttribute': PropertyAttribute,
    'PropertyAttributeEmbedding': PropertyAttributeEmbedding,
    'ParameterAttribute': ParameterAttribute,
    'ParameterAttributeEmbedding': ParameterAttributeEmbedding,
    'MetadataAttribute': MetadataAttribute,
    'MetadataAttributeEmbedding': MetadataAttributeEmbedding,
}

class EmbeddingGenerator:
    def __init__(self, file_path):
        self.file_path = file_path  # Assuming data is a CSV format text

    def parse_data(self):
        # Parse the input data into a DataFrame
        df = pd.read_csv(self.file_path, header=None)
        df.columns = ['name', 'node_name', 'embedding_cls', 'node_cls']
        return df

    def create_embeddings(self, df):
        for index, row in df.iterrows():
            input_text = row['name']
            node_name = row['node_name']
            embedding_cls = row['embedding_cls']
            node_class = row['node_cls']

            try:
                # Retrieve or create the embedding node
                try:
                    embedding_node = class_mapping[embedding_cls].nodes.get(input=input_text)
                except class_mapping[embedding_cls].DoesNotExist:
                    # If the node does not exist, create it
                    vector = request_embedding(input_text)
                    embedding_node = class_mapping[embedding_cls](input=input_text, vector=vector)
                    embedding_node.save()

                # Retrieve or create the label node
                try:
                    label_node = class_mapping[node_class].nodes.get(name=node_name)
                except class_mapping[node_class].DoesNotExist:
                    label_node = class_mapping[node_class](name=node_name)
                    label_node.save()

                # Check and create connections as necessary
                if not label_node.label.is_connected(embedding_node):
                    label_node.label.connect(embedding_node)

            except Exception as e:
                continue




if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    load_dotenv()
    from neomodel import config, MultipleNodesReturned

    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")
    # Sample CSV data
    directory = "./NodeAttributeExtraction/embedding_inputs/"
    #iterate over all csv files
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            generator = EmbeddingGenerator(directory+file)
            df = generator.parse_data()
            generator.create_embeddings(df)

{"Processing Temperature (Value)": [["Parameter"], "35.3347172791729"], "Processing Temperature (Error)": [["Parameter"], "4.03712696214248"], "Processing Temperature Unit": [["Parameter"], "K"], "Average of Processing Temperature": [["Parameter"], "31.7280001401804"], "StdDev of Processing Temperature": [["Parameter"], "3.73409186418953"], "Processing Pressure_Value": [["Parameter"], "19.3220879613495"], "Processing Pressure_Error": [["Parameter"], "4.1881390564788"], "Processing Pressure Unit": [["Parameter"], "pA"], "Processing Pressure_Average": [["Parameter"], "76.7408883367546"], "Processing Pressure_StdDev": [["Parameter"], "1.08056174498462"], "Processing Time (Value)": [["Parameter"], "48.3264537263013"], "Processing Time_Uncertainty": [["Simulation"], "1.5003712799101"], "Processing Time_Measure": [["Measurement"], "s"], "Average of Processing Time": [["Property"], "16.3510745564252"], "Processing Time_StandardDeviation": [["Property"], "9.18115037540223"], "Cooling Rate_Value": [["Parameter"], "68.7318973058018"], "Cooling Rate_Error": [["Parameter"], "3.4301429622689"], "Cooling Rate Unit": [["Parameter"], "K/s"], "Cooling Rate_Average": [["Parameter"], "76.8214144488169"], "Cooling Rate_StandardDeviation": [["Parameter"], "5.83681615492137"], "Value of Heating Rate": [["Parameter"], "27.0613215030068"], "Heating Rate_Error": [["Property"], "0.646594994979105"], "Unit of Heating Rate": [["Parameter"], "C/s"], "Heating Rate_Average": [["Parameter"], "65.5180705539552"], "Heating Rate StdDev": [["Parameter"], "1.08435962408014"], "Annealing Time_Measurement": [["Parameter"], "60.6691858347829"], "Error of Annealing Time": [["Parameter"], "0.000697334758291701"], "Annealing Time_Measure": [["Parameter"], "h"], "Annealing Time_Average": [["Parameter"], "22.9385600008208"], "Annealing Time (StdDev)": [["Parameter"], "6.42910014653806"], "Value of Annealing Temperature": [["Parameter"], "82.1197103777507"], "Annealing Temperature (Error)": [["Parameter"], "3.10668963480398"], "Annealing Temperature Unit": [["Parameter"], "C"], "Annealing Temperature Average": [["Parameter"], "91.8247225805322"], "Annealing Temperature_StdDev": [["Parameter"], "7.32233521262535"], "Value of Extrusion Speed": [["Parameter"], "5.87239505380394"], "Extrusion Speed_Error": [["Parameter"], "2.7039149925626"], "Extrusion Speed (Unit)": [["Parameter"], "h"], "Average of Extrusion Speed": [["Parameter"], "9.64997148469499"], "Extrusion Speed StdDev": [["Parameter"], "9.65399154496869"], "Rolling Speed Value": [["Parameter"], "11.9135672763019"], "Error of Rolling Speed": [["Parameter"], "2.6638190877893"], "Rolling Speed Unit": [["Parameter"], "rpm"], "Rolling Speed (Average)": [["Parameter"], "11.1668066588398"], "StdDev of Rolling Speed": [["Parameter"], "5.72347771628476"], "Molding Pressure_Value": [["Property"], "52.197798331288"], "Molding Pressure_Error": [["Property"], "0.869514285541002"], "Unit of Molding Pressure": [["Parameter"], "mpA"], "Molding Pressure_Average": [["Property"], "54.665898982461"], "StdDev of Molding Pressure": [["Parameter"], "4.14856810935466"], "Curing Time_Value": [["Parameter"], "89.3156235433893"], "Curing Time_Uncertainty": [["Parameter"], "1.76349359105749"], "Curing Time_Unit": [["Parameter"], "seconds"], "Curing Time Average": [["Parameter"], "48.5472171242446"], "StdDev of Curing Time": [["Parameter"], "0.237870756791961"], "Curing Temperature_Value": [["Parameter"], "97.8433723895535"], "Curing Temperature Error": [["Parameter"], "3.07214149796277"], "Curing Temperature (Unit)": [["Parameter"], "C"], "Curing Temperature Average": [["Parameter"], "21.2196425467225"], "Curing Temperature_StdDev": [["Parameter"], "5.29971426642602"], "Mixing Speed_Measurement": [["Parameter"], "19.0118707943174"], "Error of Mixing Speed": [["Property"], "3.6626035980142"], "Mixing Speed_Unit": [["Parameter"], "rpm"], "Mixing Speed_Mean": [["Parameter"], "46.9080616068327"], "Mixing Speed (StdDev)": [["Parameter"], "9.55230269347345"], "Mixing Time Value": [["Property"], "94.7446958051296"], "Mixing Time_Error": [["Parameter"], "2.99701280860003"], "Mixing Time_Measure": [["Measurement"], "s"], "Mixing Time_Average": [["Parameter"], "65.4498001974963"], "Mixing Time_StdDev": [["Parameter"], "9.48402223528954"], "Casting Temperature_Measurement": [["Parameter"], "29.8532888640616"], "Casting Temperature_Uncertainty": [["Parameter"], "1.71059749607566"], "Casting Temperature Unit": [["Parameter"], "min"], "Average of Casting Temperature": [["Parameter"], "36.6879410421233"], "Casting Temperature_StdDev": [["Parameter"], "9.57268643700173"], "Quenching Temperature (Value)": [["Parameter"], "93.2684555659468"], "Quenching Temperature_Uncertainty": [["Parameter"], "4.28648710322793"], "Unit of Quenching Temperature": [["Parameter"], "C"], "Quenching Temperature Average": [["Parameter"], "49.1237142156232"], "Quenching Temperature_StandardDeviation": [["Parameter"], "4.65909401782602"], "Quenching Time Value": [["Parameter"], "72.6669081079478"], "Quenching Time (Error)": [["Parameter"], "4.03684628698131"], "Quenching Time (Unit)": [["Parameter"], "h"], "Quenching Time Average": [["Parameter"], "52.6129702076008"], "StdDev of Quenching Time": [["Parameter"], "5.54316575470384"], "Aging Temperature Value": [["Parameter"], "68.8883925897427"], "Error of Aging Temperature": [["Parameter"], "3.25448340638908"], "Unit of Aging Temperature": [["Parameter"], "C"], "Aging Temperature (Average)": [["Parameter"], "38.2428385835998"], "Aging Temperature StdDev": [["Parameter"], "7.55809861210211"], "Aging Time Value": [["Metadata"], "18.5734402346152"], "Error of Aging Time": [["Parameter"], "4.83258782724323"], "Aging Time (Unit)": [["Parameter"], "h"], "Average of Aging Time": [["Parameter"], "13.6340566254569"], "Aging Time_StandardDeviation": [["Simulation"], "1.4077918148168"], "Value of Sintering Temperature": [["Parameter"], "10.5658022441941"], "Sintering Temperature Error": [["Parameter"], "2.72899763712183"], "Sintering Temperature_Unit": [["Parameter"], "C"], "Sintering Temperature (Average)": [["Parameter"], "51.7854549096266"], "StdDev of Sintering Temperature": [["Parameter"], "6.2580364740939"], "Sintering Time (Value)": [["Parameter"], "23.8916383627615"], "Sintering Time_Uncertainty": [["Parameter"], "4.44547418739647"], "Sintering Time Unit": [["Parameter"], "h"], "Sintering Time Average": [["Parameter"], "14.6056736097512"], "Sintering Time (StdDev)": [["Parameter"], "8.03261590337848"], "Milling Speed Value": [["Parameter"], "17.0491354914573"], "Error of Milling Speed": [["Parameter"], "4.28494420394006"], "Milling Speed_Measure": [["Parameter"], "s"], "Milling Speed_Mean": [["Parameter"], "83.7526012588146"], "Milling Speed_StandardDeviation": [["Parameter"], "6.23926714920175"], "Value of Milling Time": [["Parameter"], "52.5441403811947"], "Milling Time Error": [["Parameter"], "2.74989779681524"], "Milling Time_Unit": [["Parameter"], "seconds"], "Milling Time_Average": [["Measurement"], "68.3915022563348"], "Milling Time StdDev": [["Simulation"], "3.0360050473963"], "Spray Rate_Value": [["Parameter"], "66.1868226118042"], "Spray Rate_Error": [["Parameter"], "3.709945146796"], "Spray Rate (Unit)": [["Parameter"], "Parameter"], "Spray Rate_Mean": [["Parameter"], "22.9129935323929"], "Spray Rate (StdDev)": [["Parameter"], "6.99217428312462"], "Value of Deposition Rate": [["Parameter"], "37.6610124295219"], "Deposition Rate Error": [["Parameter"], "2.53884598324173"], "Unit of Deposition Rate": [["Parameter"], "-DX2K"], "Deposition Rate Average": [["Parameter"], "48.3181117250854"], "Deposition Rate (StdDev)": [["Parameter"], "9.05122174771538"], "Deposition Temperature_Value": [["Parameter"], "64.1302483042849"], "Deposition Temperature Error": [["Parameter"], "2.11592487200322"], "Deposition Temperature (Unit)": [["Simulation"], "K"], "Deposition Temperature_Average": [["Parameter"], "14.5909929134448"], "Deposition Temperature_StandardDeviation": [["Parameter"], "7.42790389611042"], "Etching Time_Value": [["Parameter"], "82.2222538718962"], "Error of Etching Time": [["Parameter"], "4.32295416793625"], "Etching Time_Unit": [["Parameter"], "Unit_Etching Time"], "Etching Time_Mean": [["Parameter"], "70.0625153319825"], "Etching Time (StdDev)": [["Parameter"], "3.0485896555861"], "Etching Temperature Value": [["Parameter"], "53.7542320991936"], "Etching Temperature Error": [["Parameter"], "0.481105555430092"], "Etching Temperature (Unit)": [["Parameter"], "Unit_Etching Temperature"], "Etching Temperature_Average": [["Parameter"], "75.6120803115259"], "Etching Temperature_StandardDeviation": [["Parameter"], "0.10205828702627"], "Plasma Power Value": [["Matter"], "35.1797379719792"], "Error of Plasma Power": [["Matter"], "4.38923817469786"], "Plasma Power_Measure": [["Matter"], "Unit_Plasma Power"], "Average of Plasma Power": [["Parameter"], "7.41379002452036"], "Plasma Power_StdDev": [["Simulation"], "4.99266590845613"], "Plasma Duration_Value": [["Parameter"], "48.5948390037031"], "Plasma Duration_Error": [["Parameter"], "0.595913140946209"], "Unit of Plasma Duration": [["Parameter"], "Unit_Plasma Duration"], "Plasma Duration Average": [["Parameter"], "37.6224355603143"], "Plasma Duration StdDev": [["Parameter"], "5.4529747892998"], "Value of Vapor Pressure": [["Property"], "16.7771753552098"], "Vapor Pressure Error": [["Property"], "2.31033461777987"], "Unit of Vapor Pressure": [["Property"], "Unit_Vapor Pressure"], "Vapor Pressure (Average)": [["Property"], "68.3572727314428"], "Vapor Pressure StdDev": [["Property"], "7.40476389956577"], "Value of Vapor Temperature": [["Property"], "83.7420731340793"], "Vapor Temperature (Error)": [["Parameter"], "1.46057480533002"], "Vapor Temperature (Unit)": [["Property"], "Unit_Vapor Temperature"], "Vapor Temperature Average": [["Property"], "24.9173094862575"], "Vapor Temperature StdDev": [["Property"], "5.11435626232182"], "Filtration Rate_Measurement": [["Parameter"], "74.6481183488095"], "Error of Filtration Rate": [["Parameter"], "2.94511436432018"], "Filtration Rate (Unit)": [["Parameter"], "Unit_Filtration Rate"], "Filtration Rate_Average": [["Parameter"], "70.7297272448863"], "Filtration Rate (StdDev)": [["Parameter"], "2.58047925976251"], "Drying Temperature Value": [["Parameter"], "92.6718843367035"], "Error of Drying Temperature": [["Parameter"], "0.144108111616946"], "Drying Temperature_Unit": [["Parameter"], "Unit_Drying Temperature"], "Drying Temperature_Average": [["Parameter"], "28.9986354341317"], "Drying Temperature_StdDev": [["Parameter"], "3.47680662520684"], "Drying Time_Measurement": [["Measurement"], "66.7138349726403"], "Drying Time Error": [["Parameter"], "0.850295872799414"], "Drying Time_Measure": [["Parameter"], "Unit_Drying Time"], "Drying Time Average": [["Parameter"], "78.6066355028894"], "StdDev of Drying Time": [["Parameter"], "0.771505799153752"], "Humidity Value": [["Parameter"], "20.6211870070023"], "Error of Humidity": [["Parameter"], "2.53842436527654"], "Humidity (Unit)": [["Parameter"], "Unit_Humidity"], "Humidity_Average": [["Parameter"], "41.4663926614043"], "Humidity_StdDev": [["Parameter"], "9.6247084886558"], "pH Value": [["Property"], "4.51596911780499"], "pH (Error)": [["Parameter"], "2.15309362365643"], "pH Unit": [["Matter"], "Unit_pH"], "pH_Average": [["Matter"], "48.3507063557195"], "pH_StdDev": [["Parameter"], "0.454137936714299"], "Solvent Concentration Value": [["Property"], "46.1285663632667"], "Solvent Concentration Error": [["Property"], "2.50986920686453"], "Solvent Concentration_Unit": [["Property"], "Unit_Solvent Concentration"], "Average of Solvent Concentration": [["Property"], "91.6323013552199"], "Solvent Concentration_StdDev": [["Property"], "4.01363169572104"], "Impurity Level_Measurement": [["Measurement"], "63.5219826128309"], "Impurity Level Error": [["Parameter"], "1.43996297686299"], "Impurity Level (Unit)": [["Measurement"], "Unit_Impurity Level"], "Impurity Level Average": [["Property"], "90.270986409976"], "Impurity Level StdDev": [["Parameter"], "8.31670879655335"], "Value of Purification Time": [["Parameter"], "81.6315491189696"], "Purification Time_Uncertainty": [["Measurement"], "3.94889866590623"], "Purification Time_Measure": [["Measurement"], "min"], "Purification Time (Average)": [["Parameter"], "70.6437337466274"], "Purification Time_StandardDeviation": [["Parameter"], "3.52513913568673"]}
