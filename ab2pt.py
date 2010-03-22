import csv

class AbDataFile(object):
	def __init__(self, file_name):
		self.file_name = file_name
		self.raw_data = file(file_name).readlines()
		self.records = list(csv.DictReader(self.raw_data))

class Ab2PtAdapter(object):
	def __init__(self, ab_data_obj):
		from dateutil.parser import parse
		self.parse_time = parse
		self.ab_data_obj = ab_data_obj

	def __getattr__(self, attr_name):
		attr_data = getattr(self.ab_data_obj, attr_name)
		new_data = list()
		if(attr_name == "records"):
			for rec in attr_data:
				if(rec["Type"] == "user story"):
					rec = self.xlate_record(rec)
					new_data.append(rec)
		return new_data
	
	def format_date(self, date_str):
		d = self.parse_time(str(date_str))
		d = d.strftime("%b %d, %Y")
		return d
	
	def fix_accepted(self, r):
		from datetime import datetime, timedelta
		accept_datetime = self.parse_time(r["Date Created"]) + timedelta(weeks=1)
		# HACK: it is always UTC, luckily
		accept_datetime = accept_datetime.replace(tzinfo=None)
		if( (accept_datetime > datetime.today()) ):
			if(r["Status"] == "Accepted"):
				accepted_str = self.format_date(datetime.today())
			else:
				accepted_str = ""
		else:
			accepted_str = self.format_date(accept_datetime)
			r["Status"] = "Accepted"
		return accepted_str
	
	def fix_estimate(self, r):
		size = r["Size"]
		if( size == "" and r["Status"] == "Accepted"):
			size = 3
		elif( size != ""):
			size = int(size)
			valid = [1,2,3,5,8]
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
		if(r["Size"] == ""):
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
		writer.writerows(self.records)
