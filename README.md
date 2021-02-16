# Protean Lite
The goal of <span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
border-radius: 5px; 
background-image: linear-gradient(to right, #D76F84, #EF86C9, #9761DB);
padding: 0.25em; 
color: white;
"> PROTEAN </span> is to provide a versatile platform for collating Threat Intelligence across an extensible range of open-source tools. A systematic evaluation of each tool was conducted to provide explanations of use-cases, functionality and incorporation into a 'pipeline' platform.

<span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
border-radius: 5px; 
background-image: linear-gradient(to right, #D76F84, #EF86C9, #9761DB);
padding: 0.25em; 
color: white;
"> PROTEAN</span> facilitates connecting an extensible range of tools, their sequential execution and the collation of individual tool outputs into a singular JSON file, or "global view".

#### Included Tools
Detailed explanations of each tool, their inputs & outputs, contributions made and any additional notes may be found in the README of each tool's subfolder. The current tools and their general purposes are:

+ <span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
width: 100px;
text-align: center;
border-radius: 5px;
background: #f0ccde;
padding: 0.25em; 
color: #303030;
font-weight: bold;
"> IOC-FINDER </span>: Grammar-based IOC Extraction
+ <span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
width: 100px;
text-align: center;
border-radius: 5px;
background: #a9c4eb;
padding: 0.25em; 
color: #303030;
font-weight: bold;
"> MACHINAE </span>: Threat Intelligence Collection

The current order is: <span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
width: 100px;
text-align: center;
border-radius: 5px;
background: #f0ccde;
padding: 0.25em; 
color: #303030;
font-weight: bold;
"> IOC-FINDER </span> -> <span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
width: 100px;
text-align: center;
border-radius: 5px;
background: #a9c4eb;
padding: 0.25em; 
color: #303030;
font-weight: bold;
"> MACHINAE </span> -> collation
#### Tool Architecture
<img style="
display: block;
width: 250px;
margin: 0 auto;"
src=/docs/images/protean_lite_architecture.png/>

## Usage
![script architecture diagram](/docs/images/protean_scripts.png)
+ **To run Protean, execute the /tools/protean/run_protean.sh**
    + The order of tool execution is defined within this script
    + This allows for certain tools to use the outputs of others (e.g. <span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
width: 100px;
text-align: center;
border-radius: 5px;
background: #a9c4eb;
padding: 0.25em; 
color: #303030;
font-weight: bold;
"> MACHINAE </span> using <span style="
display: inline-flex;
justify-content: center;
line-height: 14px;
width: 100px;
text-align: center;
border-radius: 5px;
background: #f0ccde;
padding: 0.25em; 
color: #303030;
font-weight: bold;
"> IOC-FINDER </span>'s output)

+ To promote extensibility, the current architecture executes each tool in isolated Docker containers with sequential execution orchestrated by shell scripts
+ Executing the run_protean script will prompt the user for a required information for each enabled tool
+ To use the grafana dashboard located in /docs, follow the documentation in the [Prometheus repository](https://github.com/vegasbrianc/prometheus)

#### Adding a New Tool

1. create a folder in /tools named after the new tool, *foobar*
2. create a config folder (if needed) to store python requirements / anything required during set-up or installation
3. create a src folder, this is where any scripts or Protean adaptors will be stored
4. create the *build* & *protean_runner* scripts, use existing scripts as guide
5. in tools/protean/run_protean.sh add the following at the desired execution point:
 ```(cd ../foobar; ./build.sh; ./protean_runner.sh)```

###### Connecting Tools
Connecting the inputs and outputs of tools is currently achieved through *Docker Volumes*, which allows for a directory to be persisted across containers. The following details how two tools may be connected using this method:
1. mount foobar_vol in Tool A's Docker container via the run command
2. configure Tool A to output results to /foobar_vol
3. mount foobar_vol in Tool B's Docker container via the run command
4. configure Tool B to read input from /foobar_vol


### Future Work
+ if a selection of tools is decided on for permanent use, create a Python program to handle all required input/output and run in a single container
+ utilise a messaging handler system like RabbitMQ to facilitate intercontainer communication without volumes