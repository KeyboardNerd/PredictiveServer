program ATR72;
	inputs
		speed, angle, pressure, temperature, weight (t) using closest(t);
	outputs
		weight_out: weight at every 1 sec;
  errors
  	e: (weight - pressure*speed^2*61*(6.27203070470782986234*angle+0.35713086960224765809)/(2*286.9*temperature))/weight;
  signatures
      s0(K): e = K, -0.07 < K, K < 0.07           "No error";
      s1(K): e = K, 0.07 < K, K < -0.07       "Weight sensor failure";
  correct
      s1: weight = pressure*speed^2*61*(6.27203070470782986234*angle+0.35713086960224765809)/(2*286.9*temperature);
end
