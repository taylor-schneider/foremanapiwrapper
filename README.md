# Foreman API Utilities
## Overview
The Foreman Projects is a complete lifecycle management tool for physical and virtual servers. https://www.theforeman.org/

This python package is intended to provide a simple and flexible python interface for interacting with the Foreman API v2.

This package uses the requests module to communicate with the Foreman API.

## Liscense
This project is intended to be Free and Open Source Software (FOSS)

It is distributed with the GPLv3 Liscense foud here: https://www.gnu.org/licenses/gpl-3.0.en.html

## Dependencies

The project provides relies on the following modules being installed:
* requests
* future (for python 2.7 support)

## Code and Object Model

### Records
The main object used to interact with Foreman is a "record". 
A record is a json representation of a Foreman object which is used by the API's various REST enpoints.
Examples of the types or records available are an environment, a host, a subnet, etc.
When making API calls the user is often required to supply a record or will retrieve a record as the response. 


### ForemanApiWrapper
The Foreman API does not implement all of the API endpoints in a uniform way.
This class implements an abstraction layer which provides a unified model for performing CRUD operations against the API.
It's constructor requires a username, password, url, and an boolean representing whether or not to verify SSL certificates which is useful when utilizing a self signed cert.

#### CRUD operations
All of the CRUD operations translate into API calls made by the make_api_call function.

All of the CRUD operations require the same parameter set: 

* record_type - The type of the Foreman object the user wants to interact with (eg. subnet)

* minimal_record_state - The JSON payload expected for the API call or returned by the API call.

#### Making API Calls

The make_api_call function requires that the user supply an endpoint, method, a dict object representing the json arguments, and headers. (Some of these terms are discussed later)

An API call can fail in two ways, in either case an Exception object will be thrown: 

1. An internal error occurs

    This can happen when the user misconfigured the ForemanApiWrapper and the internal python code suffered an exception
    
    For example a 400 exception because the user tried to request a URL that did not exist
   
2. A server side error occurs

    This can happen if the remote Foreman server encounters a problem.
    
    For example the server returns a 500 or 300 level error message.
    
In both cases the ForemanApiWrapper will try to construct a descriptive ForemanApiCallException 
by extracting any information that may be available from the underlying request response and attaching it
to the custom exception as fields.

#### Mapping Files
In order to unify the interfaces presented by the various API endpoints a mapping was required.
Two mapping files keep track of the data translations which need to happen based on the REST endpoint and the record type.
These are loaded when the class is instantiated and can be modified as needed.


#### ForemanApiCallException
This object will encapsulate the error that occurred while making an api call against a remote Foreman API.

The object will display the following fields.

1. endpoint

    This is the url that the exception was thrown from

2. method

    This is the HTTP method used to request the endpoint
    
3. results

    This is the result object returned from the underlying requests python module.
    
    The result object has a content attribute which contains the actual json returned by the server

4. arguments

    This is a deserialized representation of the json that was sent to the API endpoint in the request body

5. headers

    This is a dict object containing the HTTP headers that were sent to the API endpoint during the request body
     

### ApiStateEnforcer and the State Model
This class implements an idempotent interface for managing Foreman objects (records).
It allows the user to specify whether records are present or absent using a "state model".

#### State Model
In this model, the user specifies a "desired state" for a record (which can be "present" or "absent") and a
"minimal record representation" (an API compatible JSON string) which describes the record in question.
Using the CRUD functionality of the ForemanApiWrapper, the ApiStateEnforcer will interrogate the API to
ensure that  the "minimal record" is represented on the Foreman server.
In other words it will make sure a record exists (or does not exist) with the specified fields. 
Any additional fields will be ignored; hence the term "minimal".

Note: The minimal representation must contain either the name or the id of the record in question. 

#### Ensuring State

This functionality is encapsulate within the ensure_state function.

The function requires the following parameters:

* record_type - The type of the Foreman object the user wants to interact with (eg. subnet)

* desiredState - This can be "present" or "absent" to denote whether or not the minimal state should exist

* minimal_record - The JSON payload expected for the API call or returned by the API call.

The function will return a RecordModificationReceipt which will host the following fields:

* changed - a boolean representing whether or not a Write/Update was performed
* reason - a string explaining why the change was made
* minimal_record - the minimal record supplied by the user
* desired_state - the desired state supplied by the user
* actual_record - the record returned by the API if a Write/Update occurred
* original_record - the record returned by the API when a Read occurred (before any Write/Update)