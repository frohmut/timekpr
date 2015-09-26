# Timekpr: Parental time control for Ubuntu

### Timekpr-Sync: Timekpr extension to spread user configurations in the home network

To use the syncing mechanism the configuration file must
contain a new section [sync] with the entries 'getjson'
and 'postjson'.  Optionally, an entry 'timeout' can be provided
to set the timeout for the get/post requests in seconds.
The values must be full URLs to a server that hands out and
takes a json configuration description.

Two reference implementations for the server
can be found on github at https://github.com/frohmut/timekpr-server.

- one for node.js
- and one for fritzbox's ctlmgr

