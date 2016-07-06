from base import *


def test_basic():
    # read a file and assign tags (dictionary) to each column
    head, raw_data = readcsv("thetrain.csv")
    # set header information
    units = ['knot', 'in_Hg', 'celsius', 'degree', 'force_pound']
    tounits = ['m/s', 'pascal', 'kelvin', 'radian', 'newton']
    name = ['v','p','t','a','w']
    # set constant value
    constant = ['s']
    constant_value = [61.0]
    # transform unit
    transformed_data = transform_unit(raw_data, units, tounits, True)
    # stringified transformation method
    label_transformer = generate_transformer(["2*{w}/({v}**2*({p}/286.9/{t})*{s})"], name, constant, constant_value)
    feature_transformer = generate_transformer(["{a}"], name, constant, constant_value)
    # for scikit:
        # transform into Y and X
    Y = np.apply_along_axis(label_transformer, 1, transformed_data)
    X = np.apply_along_axis(feature_transformer, 1, transformed_data)
    reg = LinearRegression()
    reg.fit(X,Y)

    # prediction: load thetest.csv
    head, raw_data_test = readcsv("thetest.csv")
    # transform unit
    transformed_data_test = transform_unit(raw_data, units, tounits, True)
    X_test = np.apply_along_axis(feature_transformer, 1, transformed_data_test)
    Y_test = np.apply_along_axis(label_transformer, 1, transformed_data_test)
    plt.plot(X_test, reg.predict(X))
    plt.scatter(X_test, Y_test)
    plt.show()
    # prediction using dictionary
    prediction_name = ['a']
    prediction_data = [[1]]
    prediction_feature_transformer = generate_transformer(['{a}'], prediction_name, constant, constant_value)
    X_test = np.apply_along_axis(prediction_feature_transformer, 1, X_test)