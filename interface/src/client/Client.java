package client;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.util.HashMap;
import java.util.Map;

public class Client {
	// simple implementation of java client, currently support only one variable, more will be added...
	public static void main(String[] args){
		long startTime = System.currentTimeMillis();
		Map<String, Double> map = new HashMap<>();
		map.put("id", 1.0);
		predict(1, map);
		System.out.println("" + String.valueOf(System.currentTimeMillis() - startTime));
	}
	public static String getHTML(String url){		
		URL u;
		try {
			u = new URL(url);
			URLConnection c = u.openConnection();
			BufferedReader in = new BufferedReader(new InputStreamReader(c.getInputStream()));
			String inputLine;
			StringBuilder builder = new StringBuilder();
			while ((inputLine = in.readLine()) != null){
				builder.append(inputLine);
			}
			return builder.toString();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return null;
	}
	public static void predict(int engine, Map<String, Double> values){
		String result = send_data(engine, 2, values);
		System.out.println(result);
	}
	public static String send_data(int engine, int mode, Map<String, Double> values){
		StringBuilder builder = new StringBuilder("http://127.0.0.1:5000/?");
		for( String key : values.keySet()){
			builder.append(key + '=' + String.valueOf(values.get(key)) + '&');
		}		
		return getHTML(builder.toString());
	}
}
