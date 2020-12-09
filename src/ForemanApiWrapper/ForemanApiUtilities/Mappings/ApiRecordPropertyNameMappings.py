# As noted in the code the api endpoints provide different representations of objects (eg. GET different than PUT)
# This file contains mappings which allow us to convert actual records into minimal records (GET vs PUT/POST respectively)
# Each record type can define mappings (Only one mapping per record property)
# The mapping is as follows:
# 	"record_type": [{
# 			"minimal_record_property": "foobar",
# 			"actual_record_property": "foobar",
# 			"jsonpath": "$.record_type.foobar.[*].id",
# 			"direction": "left-to-right",
# 			"multiple_results": True
# 		}

ApiRecordPropertyNameMappings = {
	"subnet": [{
			"minimal_record_property": "domain_ids",
			"actual_record_property": "domains",
			"jsonpath": "$.subnet.domains.[*].id",
			"direction": "left-to-right",
			"multiple_results": True
		}
	],
	"provisioning_template": [{
			"minimal_record_property": "operatingsystem_ids",
			"actual_record_property": "operatingsystems",
			"jsonpath": "$.provisioning_template.operatingsystems.[*].id",
			"direction": "left-to-right",
			"multiple_results": True
		}
	],
	"operatingsystem": [{
		"minimal_record_property": "architecture_ids",
		"actual_record_property": "architectures",
		"jsonpath": "$.operatingsystem.architectures.[*].id",
		"direction": "left-to-right",
		"multiple_results": True
	},
	{
		"minimal_record_property": "ptable_ids",
		"actual_record_property": "ptables",
		"jsonpath": "$.operatingsystem.ptables.[*].id",
		"direction": "left-to-right",
		"multiple_results": True
	},
	{
		"minimal_record_property": "medium_ids",
		"actual_record_property": "media",
		"jsonpath": "$.operatingsystem.media.[*].id",
		"direction": "left-to-right",
		"multiple_results": True
	},
		{
			"minimal_record_property": "provisioning_template_ids",
			"actual_record_property": "provisioning_templates",
			"jsonpath": "$.operatingsystem.provisioning_templates.[*].id",
			"direction": "left-to-right",
			"multiple_results": True
		}
	]
}