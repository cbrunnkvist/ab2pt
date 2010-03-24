DEFAULT_ESTIMATE_WHEN_SIZE_MISSING = "2"
DEFAULT_COMPLETED_TASK_DURATION = {"days":7}

csv_headers = dict()
csv_headers["project"] = [
	"Id",
	"Title",
	"Description", 
	"Size", 
	"Priority", 
	"Feature", 
	"Release", 
	"Iteration", 
	"Source", 
	"Business Value", 
	"Business Objective", 
	"Risk", 
	"Status", 
	"Created By", 
	"Date Created", 
	"Type" 
]

csv_headers["iteration"] = [
	"Id", 
	"Title", 
	"Description", 
	"Est. Hrs", 
	"Hrs Left", 
	"Hrs Spent", 
	"Owner", 
	"Size", 
	"Priority", 
	"Feature", 
	"Status", 
	"Created By", 
	"Created", 
	"Type"
]


import csv, sys

def adapt(file_obj):
	headers = file_obj.readline().rstrip().split(",") #chop \n then split
	file_obj.seek(0)
	if(headers == csv_headers["project"]):
		return AbProject2PtAdapter(file_obj)
	elif(headers == csv_headers["iteration"]):
		return AbIteration2PtAdapter(file_obj)
	else:
		print csv_headers["iteration"]
		print headers
		raise RuntimeError("Unable to recognize CSV headers")

class Ab2PtAdapterBase(object):
	def __init__(self, file_obj):
		from dateutil.parser import parse
		self.parse_time = parse
		
		self.file_obj = file_obj
		self.raw_data = file_obj.readlines()
		self.orig_records = list(csv.DictReader(self.raw_data))
		self.orig_records.reverse()

	def format_date(self, date_str):
		d = self.parse_time(str(date_str))
		d = d.strftime("%b %d, %Y")
		return d

	def __getattr__(self, attr_name):
		new_data = list()
		if(attr_name == "records"):
			for rec in self.orig_records:
				if(rec["Type"] == "user story"):
					rec = self.xlate_record(rec)
					new_data.append(rec)
		return new_data
	
class AbIteration2PtAdapter(Ab2PtAdapterBase):
	pass

class AbProject2PtAdapter(Ab2PtAdapterBase):
	def fix_accepted(self, r):
		from datetime import datetime, timedelta
		# HACK: it is always UTC, luckily
		accept_datetime = self.parse_time(r["Date Created"]) + timedelta(**DEFAULT_COMPLETED_TASK_DURATION)
		accept_datetime = accept_datetime.replace(tzinfo=None)
		if(r["Status"] == "Accepted" or r["Status"] == "In Progress"):
			if( (accept_datetime > datetime.today()) ):
				accepted_str = self.format_date(datetime.today())
			else:
				accepted_str = self.format_date(accept_datetime)
				r["Status"] = "Accepted"
		else:
			accepted_str = ""
		return accepted_str
	
	def fix_estimate(self, r):
		size = r["Size"]
		if( size == "" and r["Status"] == "Accepted"):
			size = DEFAULT_ESTIMATE_WHEN_SIZE_MISSING
		elif( size != ""):
			size = int(size)
			valid = (0,1,2,3,5,8)
			for v in valid:
				if size <= v:
					size = v
					break
			else:
				size = valid[-1]
		r["Size"] = size
		return size
	
	def fix_status(self, r):
		status = r["Status"]
		if(r["Iteration"] == ""):
			status = "unscheduled"
		elif(r["Size"] == ""):
			status = "unscheduled"
		elif(status == "Open"):
			status = "unstarted"
		elif(status == "In Progress"):
			status = "started"
		else:
			status = status.lower()
		return status
		
	def xlate_record(self, r):
		new_rec = dict()
		new_rec["Id"] = r["Id"]
		new_rec["Story"] = r["Title"]		new_rec["Description"] = r["Description"]		new_rec["Owned By"] = (r.has_key("Owner") and r["Owner"]) or ""		new_rec["Labels"] = r["Feature"]		new_rec["Requested By"] = r["Created By"]		new_rec["Created at"] = self.format_date(r["Date Created"])		new_rec["Accepted at"] = self.fix_accepted(r)
		new_rec["Estimate"] = self.fix_estimate(r)		new_rec["Current State"] = self.fix_status(r)		new_rec["Story Type"] = "feature"
		return new_rec
	
	def write_csv(self, file_obj):
		field_names = [	
			"Id",
			"Story",
			"Description",
			"Owned By",
			"Estimate",
			"Labels",
			"Requested By",
			"Created at",
			"Current State",
			"Story Type",
			"Accepted at"
		]
		writer = csv.DictWriter(file_obj, field_names)
		writer.writerow( dict( zip(field_names,field_names) ) ) # Headers
#		print >>sys.stderr, self.records
		writer.writerows(self.records)
