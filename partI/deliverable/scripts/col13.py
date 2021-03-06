from __future__ import print_function

import sys
import string
from pyspark import SparkContext
from csv import reader
from operator import add

if __name__ == "__main__":

	def baseType_check(input):
		try:
			if type(input) == str:
				return "STRING"
		except ValueError:
			return type(input)

	def semanticType_check(value):
		try: 
			name = value.upper()		
			if (len(name) > 4 and type(name) == str):
				return "Juris Description"
			else:
				return "Other"
		except ValueError:	
				return "Other"		
			
	def validation_check(x):
		x = x.upper()
		if x == '':
			return "NULL"
		elif (len(x) > 4 and type(x) == str):
			return "VALID"
		else:	
			return "INVALID"
    # Collect the statistics
	def statistic_count(rdd, baseType_check, semanticType_check, validation_check):
		rdd.map(lambda row: (row, 1)) \
			.reduceByKey(lambda x, y: x + y) \
			.sortBy(lambda x: x[1]) \
			.map(lambda row: (row[0], baseType_check(row[0]), semanticType_check(row[0]), validation_check(row[0]), row[1])) \
			.saveAsTextFile("col13_statistic_count.out")
	
	sc = SparkContext()

	lines = sc.textFile(sys.argv[1], 1)

	header = lines.first()
	# Remove the header
	lines = lines.filter(lambda x: x!=header).mapPartitions(lambda x: reader(x))

	lines = lines.map(lambda x: (x[12]))
	# Statistic VALID, INVALID, and NULL values 
	validation_count = lines.map(lambda x: (validation_check(x), 1)) \
		.reduceByKey(lambda x, y: x + y)

	validation_count.saveAsTextFile("col13_validation_count.out")
	# Collect the statistics
	statistic_count(lines, baseType_check, semanticType_check, validation_check)

	sc.stop()