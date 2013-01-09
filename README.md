# remoteconf

Env file for foreman and honcho served through http
These are simple servers that use redis to store environment data and generate them dynamically per request. They also contain a .ini file generator that I've not put too much effort.
The objective is to avoid having a .env file that needs to be kept in some place and might contain sensitive information as API keys and passwords.
Ideally this server would run internally, using https or extended to have a kind of challenge/response to make it safer.
Both servers depend on redis.

URL might be either http://localhost:5000 or http://localhost:9292 if it's the sinatra app

curl -X POST -d 'appname=test' http://localhost:5000/app/delete # removes an application

curl -X POST -d 'appname=test' http://localhost:5000/app/new # creates a new application

curl -X POST -d 'key=parameter1&val=value1' http://localhost:5000/env/test # add key/value parameters
curl -X POST -d 'key=parameter2&val=value2' http://localhost:5000/env/test
curl -X POST -d 'key=parameter3&val=value3' http://localhost:5000/env/test

curl http://localhost:5000/env/test # dump an env file
curl http://localhost:5000/ini/test # dump an ini file
curl -X POST -d 'key=newsection.parameter1&val=value1' http://localhost:5000/env/test
curl http://localhost:5000/ini/test # dump an ini file

The dot on the key parameter will act as a section to the ini file view. To the env file view it will keep the full key name.

Gleicon


