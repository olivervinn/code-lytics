#Proj-Lytics

Set of scripts to aggregate information from Jenkins, Coverity and QAC - mergining data into a single source for presenting with a simple web 
interface.

![](https://raw.github.com/ovinn/proj-lytics/master/img/example.png)


#Use

Configure scripts with details of your web instances of Jenkins, Coverty plus login credentials. 
Generates a <file>.json

* clrunner
  * Fetches and merges data source to produce a single json representation
* cljenkins
  * Gets warnings for a job
* clcoverity
 * Gets component map
 * Gets issues
* clutils
 * Convertions
 * Finger print local files (HASH)

Place in home directory of website

> pyton -m SimpleHTTPServer

Go to URL

> http://localhost:8000
