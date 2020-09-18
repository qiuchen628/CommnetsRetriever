from os import listdir
from os.path import isfile, join
import pandas
mypath = '/Users/chenqiu/PycharmProjects/CommnetsRetriever/files'

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
files = [x[:11] for x in onlyfiles]

print(onlyfiles)
print(files)

table1 = pandas.read_csv('/Users/chenqiu/PycharmProjects/CommnetsRetriever/data/raw_table.csv')
raw_list = list(table1['Example_Youtube_Link'])
raw_list2 = [x[-11:] for x in raw_list]
print(raw_list2)

print(set(raw_list2) - set(files))

print(set(files) - set(raw_list2))