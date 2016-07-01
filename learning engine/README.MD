transformer:
defines how to transform the feature, label data to desired data format
optimizer:
defines how to 
model string: (MODE 0)
define 1. which learning model to be used, 2. what preprocessing will be took
FEATURE: list of strings: how to compute each feature
LABEL: string: how to compute label

training string: (MODE 1)
define 1. query of data 2. how to relate queried data to feature/label 3. what running pipeline will be used

predict string: (MODE 2)
define 1. what running pipeline will be used, 2. what value will be used for prediction.

e.g.
~~~~
model_define_string = '{"MODE": 0, "ID":0, "MODEL":"My regression 1", "FEATURE":["{aoa}"], "LABEL":"2*{W}/({V}**2*{S}*(4.174794718087996e-11*(288.14-0.00649*{H})**4.256))"}'

training_string_db = '{"MODE": 1, "ID": 0, "OBJECT":"example", "size":1000,"DATA":"aoa=angle of attack(radian),  W=current weight(N), V=true air speed(m/s), S=61.0(m^2), H=altitude msl(m)","CONSTRAINT": "abs({b}-{a})/{a}<0.01, b=lift(N), a = current weight(N)"}'

predict_string = '{"MODE": 2, "ID": 0, "VALUES":[0.02234021]}'
~~~~
TODO:
1. simplify code to support more complex learning libraries and distributed frameworks like hadoop
2. test more complex learning models
3. support streaming data
4. use pickle to serialize learning model algorithms