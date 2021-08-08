# Maven Dependency Parser
A python based parser from the output of `mvn dependency:tree`.

# Requirements
Python 3.x

# Usage
1. Build a depedency tree of a maven project with `mvn dependency:tree -DoutputFile=<path-to-file>`. See details on maven dependency plugin page 
http://maven.apache.org/plugins/maven-dependency-plugin/usage.html#dependency:tree
2. Run script as
```bash
python dependency_parser.py -f test.txt --dependency "<dependency_name>"
```



