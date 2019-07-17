ApiRecordPropertyNameMappings = {
	"subnet": [{
			"minimal_record_property" : "domain_ids",
			"actual_record_property": "domains",
			"jsonpath": "$.subnet.domains.[*].id",
			"direction": "left-to-right",
			"multiple_results": True
		}
	],
	"provisioning_template": [{
			"minimal_record_property" : "operatingsystem_ids",
			"actual_record_property": "operatingsystems",
			"jsonpath": "$.provisioning_template.operatingsystems.[*].id",
			"direction": "left-to-right",
			"multiple_results": True
		}
	]
}