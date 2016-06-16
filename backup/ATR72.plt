program ATR72;
	inputs
		speed, height, weight (t) using closest(t);
	outputs
		weight_out: weight at every 1 sec;
  errors
  	e: (weight - (101.29*(((15.04 - 0.00649*height) + 273.1)/288.08)^5.256)*speed^2*61*(6.27203070470782986234*0.03+0.35713086960224765809)/(2*286.9*(15.04 - 0.00649*height)))/weight;
  signatures
      s0(K): e = K, -0.07 < K, K < 0.07           "No error";
      s1(K): e = K, 0.07 < K, K < -0.07       "Weight sensor failure";
  correct
      s1: weight = (weight - (101.29*(((15.04 - 0.00649*height) + 273.1)/288.08)^5.256)*speed^2*61*(6.27203070470782986234*0.03+0.35713086960224765809)/(2*286.9*(15.04 - 0.00649*height)));
end
