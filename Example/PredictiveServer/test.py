import csv

from IH.ENG.engineIO import *

env = train_model("definitions/regression_config.json")
wr = csv.writer(open("regression_label.csv", 'w+'), delimiter=',')
wr.writerows(env.label.tolist())
wr = csv.writer(open("regression_feature.csv", 'w+'), delimiter=',')
wr.writerows(env.feature.tolist())
"""
env = train_model("definitions/bayes_config.json")
label = env.label.tolist()
feature = env.feature.tolist()
wr = csv.writer(open("bayes_label.csv",'w+'), delimiter=',')
wr.writerows(label)
wr = csv.writer(open("bayes_feature.csv",'w+'), delimiter=',')
wr.writerows(feature)
predicted, env = test_model("definitions/bayes_config_test.json")
wr = csv.writer(open("bayes_testing_feature.csv",'w+'), delimiter=',')
wr.writerows(env.feature.tolist())
wr = csv.writer(open("bayes_testing_result.csv",'w+'), delimiter=',')
wr.writerows(predicted.tolist())
plt.plot(predicted.T.tolist()[0])
plt.show()
"""