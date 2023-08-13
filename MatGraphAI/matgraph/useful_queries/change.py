import re
from csv import reader, writer
formula = "C12HO"
Atoms = (['C', 'H', 'O', 'N', 'F', 'Cl', 'P', 'Br', 'I', 'S', 'V'])
Atomlist = {}
rows = []
with open('../data/materials/PubChemMolecules.csv', 'r') as read_obj:
    csv_reader = reader(read_obj)
    next(csv_reader)
    for row in csv_reader:
        Atomdict = {'C' : '', 'H': '', 'O': '', 'N': '', 'F': '', '0': '', 'Cl': '', 'P': '', 'Br': '', 'I': '', 'S': '', 'V': ''}
        print(row)
        res = re.findall('[A-Z][^A-Z]*', row[4])
        for ding in res:
            if not ding[-1].isdigit():
                ding = ding + "1"
            ding1 = re.split('([-+]?\d+\.\d+)|([-+]?\d+)', ding.strip())
            ding2 = [r.strip() for r in ding1 if r is not None and r.strip() != '']
            Atomdict[ding2[0]] = ding2[1]
            Atomlist[ding2[0]]= None
            print(Atomdict)
            row[24] = Atomdict['C']
            row[25] = Atomdict['H']
            row[26] = Atomdict['O']
            row[27] = Atomdict['N']
            # row[22] = Atomdict['F']
            # row[23] = Atomdict['Cl']
            # row[24] = Atomdict['P']
            # row[25] = Atomdict['Br']
            # row[26] = Atomdict['I']
            # row[27] = Atomdict['S']
            # row[28] = Atomdict['V']
        rows.append(row)

        print(row)
print(Atomlist)
            # Atomdict[ding2[0]] = ding2[1]
with open('../data/materials/PubChemMolecules_sum.csv', 'w') as read_obj:
    csv_reader = writer(read_obj)
    csv_reader.writerows(rows)

