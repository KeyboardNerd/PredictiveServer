# define middleware structure on top of previous code
class Pipeline():
    def __init__(self, methods, loopable=False, name=''):
        self.methods = methods
        self.name = name
        self.loopable = loopable
        self.env = {}
        self.current_step = 0
        self.inputenv = {}
    def feed(self, data={}):
        self.inputenv.update(data)
        self.env.update(data)
        return self
    def forward(self):
        self.methods[self.current_step](self.env)
        self.current_step += 1
        if self.loopable and self.current_step == len(self.methods):
            self.current_step = 0
        return self
    def fastforward(self):
        while (self.current_step < len(self.methods)):
            self.methods[self.current_step](self.env)
            self.current_step += 1
        if self.loopable:
            self.current_step = 0
        return self
    def record(self):
        if self.current_step > 0:
            self.current_step -= 1
        return self
    def reset(self):
        self.current_step = 0
        return self
    def current(self):
        if self.current_step >= len(self.methods):
            raise Exception("All steps are done")
        return ( self.methods[self.current_step], self.current_step )

def pipe_readcsv(in_):
    head, raw_data = readcsv(in_['file'])
    in_['head'] = head
    in_['raw_data'] = raw_data
def pipe_transform_unit(in_):
    in_['transformed_data'] = transform_unit(in_['raw_data'], in_['units'], in_['tounits'], True)
def pipe_transform(in_):
    in_['label_transformer'] = generate_transformer(in_['labels'], in_['name'], in_['constant'], in_['constant_value'])
    in_['feature_transformer'] = generate_transformer(in_['features'], in_['name'], in_['constant'], in_['constant_value'])
    in_['Y'] = np.apply_along_axis(in_['label_transformer'], 1, in_['transformed_data'])
    in_['X'] = np.apply_along_axis(in_['feature_transformer'], 1, in_['transformed_data'])
def pipe_model_regression(in_):
    reg = LinearRegression()
    in_['model'] = reg
def pipe_model_train(in_):
    in_['model'].fit(in_['X'], in_['Y'])

def pipe_model_make_predictor(in_):
    pipeline = Pipeline([pipe_predict_transform, pipe_predict_predict])
    pipeline.env['model'] = in_['model']
    pipeline.env['features'] = in_['features']
    pipeline.env['constant'] = in_['constant']
    pipeline.env['constant_value'] = in_['constant_value']
    in_['predictor'] = pipeline

def pipe_predict_transform(in_):
    in_['feature_transformer'] = generate_transformer(in_['features'], in_['name'], in_['constant'], in_['constant_value'])
    in_['value'] = np.apply_along_axis(in_['feature_transformer'], 1, in_['value'])

def pipe_predict_predict(in_):
    in_['result'] = in_['model'].predict(in_['value'])

def pipe_visualize(in_):
    model = in_['model']
    plt.plot(model.predict(in_['X']), in_['X'])
    plt.scatter(in_['Y'], in_['X'], marker='.')
    plt.show()

def test_pipe():
    # define training data:
    to_data = {"file": "thetrain.csv", "name": ['v','p','t','a','w'], 'constant': ['s'], 'constant_value':[61.0] }
    # define unit conversion:
    to_transunit = {"units": ['knot', 'in_Hg', 'celsius', 'degree', 'force_pound'],
                    "tounits": ['m/s', 'pascal', 'kelvin', 'radian', 'newton']}
    to_transformer = {"labels": ["2*{w}/({v}**2*({p}/286.9/{t})*{s})"], "features": ["{a}"]}
    to_instance = {"trainer": "testpipeline"}
    global TRAINER
    # define learning pipe line in use:
    trainer = Pipeline('testpipeline', [pipe_readcsv, pipe_transform_unit, pipe_transform, pipe_model_regression, pipe_model_train, pipe_model_make_predictor])
    predictor = Pipeline('testpredictor', [pipe_predict_transform, pipe_predict_predict])
    trainer.feed(to_data)
    trainer.feed(to_transunit)
    trainer.feed(to_transformer)
    trainer.fastforward()

    to_predict_this = {"predictor": "testpipeline", "name": ['a'], "value": trainer.env['X']}
    X = trainer.env['X']
    Y = trainer.env['Y']
    # retrieve predictor
    predictor = trainer.env['predictor']
    PREDICTOR['testpipeline'] = predictor
    predicted = PREDICTOR[to_predict_this['predictor']].feed(to_predict_this).fastforward().env['result']
    plt.plot(X, predicted)
    plt.scatter(X, Y, marker='x', color='r')
    plt.show()