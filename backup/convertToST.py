import datetime
def f(filename):
    x = open(filename,"rU")
    x_out = open(filename+".pltdata","w+")
    l = x.readlines()
    x_out.write('#true_air_speed,ambient_pressure,ambient_temperature,angle_of_attack,weight\n')
    for i in xrange(1,len(l)):
        x_out.write(datetime.datetime.fromtimestamp(100000).strftime(':%Y-%m-%d %H%M%S000-0400:') + l[i])
f("data/ATR72_testing.csv")
