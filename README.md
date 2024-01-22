# AQLabs Mini Pipeline

This CI/CD Pipeline was developed to stream-line the continuous development and continuous deployment of spring-boot applications.

Using Python, for its ease of system manipulation, and using a lightweight server like Flask and a tiny-bit of Multi-Threading brings this customizable mini pipeline. 

## How to prepare to use it

First off you need a way for Git-Hub to send a webhook to the running Flask server. Git-hub uses port 3000 to send webhooks

If you are using a Virtual-Machine to deploy the application you need to have incoming requests open to port 3000

Set up a webhook for your project on Git-Hub and have it send it to http://your-server-public-ip:3000/webhook. Git-Hub will send a POST request to the flask server running on that IP and start the pipeline

I have created a youtube video on how to use it here -> https://www.youtube.com/watch?v=u55UV1-rmBA
## Make sure you have
- Java installed
- Docker installed
- Git installed
- Docker compose installed
- Pip installed
- Flask installed via Pip
- You are able to push and pull from the server getting deployed too (you may have to set up SSH key with Git-Hub)


## Notes

The pipeline will check to see if your repository contains:
- minipipe.json [ Configuration File]
- secrets.json [Used fro API keys]
- dockerfile [Used to create the Image]


## minipipe.json
This is the configuration file the pipeline will use to configure your Docker container name and Docker image name

To get the 'output_jar' file name
 1. In your Spring-Boot project locate the pom.xml
 2. Find the tags \<artifactId\> and \<version\>
 3. combine the tags values together 

For example in pom.xml
```html	
    <artifactId>cookbook</artifactId>
    <version>0.0.1-SNAPSHOT</version>
```

output_filename = cookbook-0.0.1-SNAPSHOT

How it looks:
```json
{
  "container_name": "name-of-container",
  "image_name": "name-of-image",
  "output_filename": "name-of-output-jar-file",
  "args": "-d -p 8080:8080"
}
```
