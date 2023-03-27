import csv
# Parse and return the keyword from the csv file

# The thing I'm looking for
keyword = 'A'


# open and read the csv file
# csv_file = csv.reader(open('test.csv', 'r'), delimiter=',')

with open('test.csv') as csv_file_obj:
    file_reader = csv.reader(csv_file_obj, delimiter=',')

    # search the csv file for the keyword
    # loop through the csv file
    for row in file_reader:
        # if the current row is equal to the input, retun the input
        if keyword == row[0]:
            print(row)


# https://stackoverflow.com/questions/26082360/python-searching-csv-and-return-entire-row
