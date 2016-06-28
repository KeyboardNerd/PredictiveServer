# PredictiveServer
Derived from WCL Learning model. This project will grow as a standalone predictive server

Target: construct a generic interface for different predictive model frameworks like Tensorflow, and accepting serialized query. 

Current: 
  database is sqlite3 database and holding special homogenerous X-Plane flying data, this is designed specifically for PILOTS. 
  learning model can be defined by register_model(name, model), in which the model should have interface fit() and predict().
  preprocessor can be defined by String like "{a} - {b}" and use part of database query "a=angle of attack, b=bacon" to link preprocessor with queried data
  predict can be done by string like "a=1.2, b=3.4"
  query should identify which object, what data (unit) and what constraint on the size of queried data or other constraint to filter the queried data.

problems:
  it's still a proof of concept to stringify the learning process, tested only with small faction of data/models in scikit and X-Plane data. The framework is homebrew, not so good.
