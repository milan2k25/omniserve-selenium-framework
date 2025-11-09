import csv

def read_csv_file(path,delimiter_value):
    with open(path) as f:
        data = csv.reader(f,delimiter=delimiter_value)
        csv_data=[]
        for row in data:
            csv_data.append(row)
    return csv_data

def write_into_csv_file(path,data):
    with open(path,'a',newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
