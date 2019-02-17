# Foreman API Wrapper
## Overview
The Foreman Projects is a complete lifecycle management tool for physical and virtual servers. https://www.theforeman.org/

This python package is intended to provide a simple and flexible python interface for interacting with the Foreman API v2.

It is built on the requests module.
## Liscense
This project is intended to be Free and Open Source Software (FOSS)

It is distributed with the GPLv3 Liscense foud here: https://www.gnu.org/licenses/gpl-3.0.en.html
## Dependencies

The project provides relies on the following modules being installed:
* requests
* future (for python 2.7 support)

## Object Model
There are two main objects in this project. 

### ForemanAPIWrapper
The ForemanApiWrapper object which is responsible for storing connection details and making API calls to a Foreman instance. 

It's constructor requires a username, passeord, url, and an boolean representing whether or not to verify SSL certificates which is useful when utilizing a self signed cert.

To make an api call the user must supply an endpoint, method, a dict object representing the json arguments, and headers. (Some of these terms are discussed later)

An API call can fail in two ways, in either case an Exception object will be thrown: 

1. An internal error occurs

    This can happen when the user misconfigured the ForemanApiWrapper and the internal python code suffered an exception
    
    For example a 400 exception because the user tried to request a URL that did not exist
   
2. A server side error occurs

    This can happen if the remote Foreman server encounters a problem.
    
    For example the server returns a 500 or 300 level error message.
    
In both cases the ForemanApiWrapper will try to construct a descriptive ForemanApiCallException by extracting any information that may be available from the underlying request response.
### ForemanApiCallException
This object will encapsulate the error that occured while making an api call against a remote Foreman API.

The object will contain the following pieces of information
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
     
