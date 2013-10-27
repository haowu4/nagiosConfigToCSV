""" Transfer Nagios3 config file to csv """

__author__  = "Hao Wu"


import os.path 
from os import listdir
import sys

def load_file(path):
	f = open(path)
	content = []
	for line in f:
		if line.strip().startswith("#"):
			pass
		else:
			content.append(line.strip())

	return content

def parse_file(content):
	# a State Machine, 
	# States:
	#  1. Begin
	#  2. Middle
	#  3. End
	#  4. Other
	state = 0
	obj_list = []
	for line in content:

		if state is 3:
			pass

		if line.startswith("define") and line.endswith("{"):
			state = 1
			obj = {}
			obj["type"] = line[6:-1].strip()
			obj["data"] = {}
			# print obj["type"]
			continue
		if line.startswith("}") and state is 2:
			state = 3
			obj_list.append(obj)

			continue
		if state is 1:
			state = 2

		if state is 2:
			try:
				sidx = line.index(" ")
			except ValueError,e:
				sidx = 999999
					
			try:
				tidx = line.index("	")
			except ValueError,e:
				tidx = 999999
			idx = min(sidx,tidx)
			key = line[:idx]

			value = line[idx:].strip()
			if "," in value:
				value = '"'+value.replace(",",",\n")+'"'

			obj["data"][key] = value
	return obj_list

def process_dir(path):
	filelist = list_all_file(path)
	config_list = []
	for f in filelist:
		c = load_file(f)
		ret = parse_file(c)
		config_list += ret
	print len(config_list)
	return config_list


def list_all_file(mypath):
	onlyfiles = [ os.path.join(mypath,f) for f in listdir(mypath) if os.path.isfile(os.path.join(mypath,f)) ]
	return onlyfiles

def get_all_type(data):
	ret = set()
	for d in data:
		ret.add(d["type"])

	return ret

def get_all_config_by_type(data,type_str):
	ret = []
	for d in data:
		# print d["type"]
		# print type_str
		if d["type"].strip() == type_str.strip():
			# print d
			ret.append(d["data"])
	# print len(data)

	# print type_str
	print len(ret)
	return ret

def generate_json(config_dir,output):
	data = process_dir(config_dir)
	type_set = get_all_type(data)
	for typ in type_set:
		# print typ
		configs = get_all_config_by_type(data,typ)
		ret = build_csv(configs)
		fo = open(os.path.join(output,typ+".csv"),"w")
		for line in ret:
			fo.write(line+"\n")




def find_column(data):
	ret = []
	for d in data:

		for k in d.keys():
			if k not in ret:
				ret.append(k)
			else:
				pass
	# print ret
	return ret

def build_csv(data):
	ret = []
	col = find_column(data)
	ret.append(",".join(col))
	row_leng = len(col)
	for d in data:
		row = [""]*row_leng
		for k in d.keys():
			idx = col.index(k)

			row[idx] = d[k]
		ret.append(",".join(row))

	return ret



if __name__ == "__main__":
	try:
		input_dir = sys.argv[1]
		if input_dir == "help":
			i = 2/0
		output_dir = sys.argv[2]
		generate_json(input_dir,output_dir)
		# generate_json("config","out")
	except Exception as inst:
		print "Help info: "
		print "		run with the following: "
		print "		$ python generate.py [nagios config folder] [output folder]"
		print "	For example:"
		print "		$ python generate.py /etc/nagios3/conf.d/ ~/output"