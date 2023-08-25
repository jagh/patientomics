
import csv

# Read the CSV file
file_name='lab_patient_1000007'
with open('/home/jagh/Documents/01_UB/MultiOmiX/patientomics/examples/' + file_name + '.csv', 'r') as file:
    reader = csv.reader(file)
    table_data = list(reader)

# Get the header row and remove the 'lab_name' column
header = table_data[0][1:]
table_data = table_data[1:]

# Sort the header based on the day number
sorted_header = sorted(header, key=lambda col: int(col.split('-')[1]))

# Reconstruct the table data with sorted columns
sorted_table_data = [[row[0]] + [row[header.index(col) + 1] for col in sorted_header] for row in table_data]

# Print the sorted table
for row in sorted_table_data:
    print('\t'.join(row))

# Write the sorted table to a new CSV file
with open('/home/jagh/Documents/01_UB/MultiOmiX/patientomics/examples/' + file_name + '_sorted.csv', 'w') as file:
    ## added the header line seperately by ','
    file.write('lab_name,' + ','.join(sorted_header) + '\n')
    writer = csv.writer(file)
    writer.writerows(sorted_table_data)
    