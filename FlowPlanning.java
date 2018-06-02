import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Scanner;

public class FlowPlanning {
	
	private final int x;
	private final int y;
	private final int z;
	
	private String lp = "";
	private String lpFile = "assignment2.lp";
	private String lpText = "assignment2.txt";


	/**
	 * returns the header text
	 * @return String
	 */
	static String Header(){
		return "Minimize\n\tr\nSubject to\n";
	}
	
	
	/**
	 * demand volume from src node Si to dest node Dj
	 * "between src node Si (1<=i<=X) and dst node Dj (1<=j<=Z) there is a demand volume of Hij = i + j"
	 * @param x
	 * @param y
	 * @param z
	 * @return String
	 */
	static String demandVolumeConstraints(int x, int y, int z){
		String constraints = "";
		// src
		for(int i = 1; i <  x+1; i++){
			// dst
			for(int j = 1; j < z+1; j++){
				// trans
				for(int k = 1; k < y+1; k++){
					// first statement
					if(k==1){
						constraints += String.format("DemandVolume%d%d: x%d%d%d",i, j, i, k, j);
					}
					// middle statements
					else if(k < y){
						constraints += String.format(" + x%d%d%d", i, k, j);
					}
					// end statement
					else{
						constraints += String.format(" + x%d%d%d = %d\n", i, k, j, i+j);
					}
				}
			}
		}
		return constraints;
	}
	
	
	/**
	 * demand flow from src node Si to dst node Dj - limits to 3 trans nodes
	 * @param x
	 * @param y
	 * @param z// https://stackoverflow.com/questions/16714127/how-to-redirect-process-builders-output-to-a-string
	 * @return String
	 */
	static String demandFlowConstraints(int x, int y, int z){
		String constraints = "";
		// src
		for(int i = 1; i < x+1; i++){
			// dst
			for(int j = 1; j < z+1; j++){
				// trans
				for(int k = 1; k < y+1; k++){
					constraints += String.format("DemandFlow%d%d%d: 3 x%d%d%d - %d u%d%d%d = 0\n", i, k, j, i, k, j, i+j, i, k, j);
				}
			}
		}
		return constraints;
	}
	
	
	/**
	 * constraints for the src - trans link
	 * "for a link between src node Si and trans node Tk we denote the capacity by Cik"
	 * @param x
	 * @param y
	 * @param z
	 * @return String
	 */
	static String srcNodeConstraints(int x, int y, int z){
		String constraints = "";
		// src
		for(int i = 1; i < x+1; i++){
			// trans
			for(int k = 1; k < y+1; k++){
				//dst
				for(int j = 1; j < z+1; j++){
					// first statement
					if(j==1){
						constraints += String.format("SrcConstraints%d%d: x%d%d%d",i , k, i, k, j);
					}
					// middle statements
					else if(j < z){
						constraints += String.format(" + x%d%d%d", i, k, j);
					}
					// end statement
					else {
						constraints += String.format(" + x%d%d%d - st%d%d = 0\n", i, k, j, i, k);
					}
				}
			}
		}
		return constraints;
	}
	
	
	/**
	 * constraints for the trans - dst link
	 * @param x
	 * @param y
	 * @param z
	 * @return String
	 */
	static String dstNodeConstraints(int x, int y, int z){
		String constraints = "";
		// trans
		for(int k = 1; k < y+1; k++){
			// dst
			for(int j = 1; j < z+1; j++){
				// src
				for(int i = 1; i < x+1; i++){
					// first statement
					if(i==1){
						constraints += String.format("DstConstraint%d%d: x%d%d%d",k, j, i, k, j);
					}
					// middle statements
					else if(i < x){
						constraints += String.format(" + x%d%d%d", i, k, j);
					}
					// end statement
					else{
						constraints += String.format(" + x%d%d%d - td%d%d = 0\n", i, k, j, k, j);
					}
				}
			}
		}
		return constraints;
	}
	
	
	static String transNodeConstraints(int x, int y, int z) {
		String constraints = "";
		// trans
		for(int k = 1; k < y+1; k++){
			// src 
			for(int i = 1; i < x+1; i++){
				// dst
				for(int j = 1; j < z+1; j++){
					// first statement
					if(j==1 && i == 1){
						constraints += String.format("TransConstraint%d: x%d%d%d", k, i, k, j);
					}
					// middle statements
					else if(j < z || i < x){
						constraints += String.format(" + x%d%d%d", i, k, j);
					}
					// end statement
					else {
						constraints += String.format(" + x%d%d%d - r <= 0\n", i, k, j);
					}
				}
			}
		}
		return constraints;
	}
	
	/**
	 * limits link utilization to 3
	 * uses binaries to set the total number of available paths
	 * @param x
	 * @param y
	 * @param z
	 * @return String
	 */
	static String utilisationConstraints(int x, int y, int z){
		String constraints = "";
		// src
		for(int i = 1; i < x+1; i++){
			// dst
			for(int j = 1; j < z+1; j++){
				// trans
				for(int k = 1; k < y+1; k++){
					// first statement
					if(k==1){
						constraints += String.format("Utilisation%d%d: u%d%d%d", i, j, i, k, j);
					}
					// middle statements
					else if(k < y){
						constraints += String.format(" + u%d%d%d", i, k, j);
					}
					// end statement
					else{
						constraints += String.format(" + u%d%d%d = 3\n", i, k, j);
					}
				}
			}
		}
		return constraints;
	}
	
	
	/**
	 * bounds for .lp file
	 * all parameters have to be greater than 0
	 * @param x
	 * @param y
	 * @param z
	 * @return String
	 */
	static String bounds(int x, int y, int z){
		//String bounds = "\nBounds\nr >= 0\nr <= 1\n";
		String bounds = "\nBounds\nr >= 0\n";
		// src
		for(int i = 1; i < x+1; i++){
			// trans
			for(int k = 1; k < y+1; k++){
				// dst
				for(int j = 1; j < z+1; j++){
					bounds += String.format("x%d%d%d >= 0\n", i, k, j);
				}
			}
		}
		// src
		for(int i = 1; i < x+1; i++){
			// trans
			for(int k = 1; k < y+1; k++){
				bounds += String.format("st%d%d >= 0\n", i, k); 
			}
		}
		// trans
		for(int k = 1; k < y+1; k++){
			// dst
			for(int j = 1; j < z+1; j++){
				bounds += String.format("td%d%d >= 0\n", k, j);
			}
		}
		
		return bounds;
	}
	
	
	/**
	 * binaries for .lp file
	 * 0 = not included in the 3 route paths
	 * 1 = included in the 3 route paths
	 * @param x
	 * @param y
	 * @param z
	 * @return String
	 */
	static String binaries(int x, int y, int z){
		String binaries = "\nBinary\n";
		// src
		for(int i = 1; i < x+1; i++){
			// trans
			for(int k = 1; k < y+1; k++){
				// dst
				for(int j = 1; j < z+1; j++){
					binaries += String.format("u%d%d%d\n", i, k, j);
				}
			}
		}
		binaries += "\nEnd";
		return binaries;
	}
	
	
	static String cplex(String file){
		// https://stackoverflow.com/questions/15356405/how-to-run-a-command-at-terminal-from-java-program
		
		// for repository
		//String[] pathAndArgs = new String[] {"/home/cosc/student/jli231/Documents/COSC364/CPLEX/cplex/bin/x86-64_linux/cplex", "-c", "read /home/cosc/student/jli231/Documents/COSC364/COSC364-Assignment-/"+file, "optimize", "display solution variables -"};
		
		// for eclipse workspace
		String[] pathAndArgs = new String[] {"/home/cosc/student/jli231/Documents/COSC364/CPLEX/cplex/bin/x86-64_linux/cplex", "-c", "read /home/cosc/student/jli231/eclipse-workspace/COSC364/"+file, "optimize", "display solution variables -"};
		//String[] pathAndArgs = new String[] {"/home/cosc/student/jli231/Documents/COSC364/CPLEX/cplex/bin/x86-64_linux/cplex", "-c", "read /home/cosc/student/jli231/eclipse-workspace/COSC364/"+file, "optimize", "display conflict all"};
		
		String result = "";
		
		try {
			// https://stackoverflow.com/questions/5711084/java-runtime-getruntime-getting-output-from-executing-a-command-line-program#answer-5711150
			Runtime rt = Runtime.getRuntime();
			Process proc = rt.exec(pathAndArgs);

			// for successful result - read the output from the command
			BufferedReader stdInput = new BufferedReader(new InputStreamReader(proc.getInputStream()));
			String s = null;
			while ((s = stdInput.readLine()) != null) {
				result += s;
			    System.out.println(s);
			}
	
			// for unsuccessful result - read any errors from the attempted command
			BufferedReader stdError = new BufferedReader(new InputStreamReader(proc.getErrorStream()));
			while ((s = stdError.readLine()) != null) {
			    System.out.println(s);
			}
		}
		catch (IOException e) {
			System.out.println("Could not open Process and/or BufferedReader\n");
			e.printStackTrace();
			System.exit(1);
		}
		return result;
	}
	
	
	/** 
	 * constructor
	 * @param src
	 * @param trans
	 * @param dst
	 */
	public FlowPlanning(int src, int trans, int dst) {
		x = src;
		y = trans;
		z = dst;
	}
	
	
	/**
	 * main
	 * @param args
	 */
	public static void main(String[] args) {
		int src;
		int trans;
		int dst;
		// if args have been entered from command line
		if(args.length == 3){
			src = Integer.parseInt(args[0]);
			trans = Integer.parseInt(args[1]);
			dst = Integer.parseInt(args[2]);
		}
		// if running in console
		else {
			Scanner sc = new Scanner(System.in);
			System.out.println("how many src nodes?: ");
			src = sc.nextInt();
			System.out.println("how many trans nodes?: ");
			trans = sc.nextInt();
			System.out.println("how many dst nodes?: ");
			dst = sc.nextInt();
			sc.close();	
		}
		// new Flow Planning instance
		FlowPlanning lp = new FlowPlanning(src, trans, dst);
		
		// create lp string 
		lp.lp += Header();
		lp.lp += demandVolumeConstraints(lp.x, lp.y, lp.z);
		lp.lp += demandFlowConstraints(lp.x, lp.y, lp.z);
		lp.lp += srcNodeConstraints(lp.x, lp.y, lp.z);
		lp.lp += dstNodeConstraints(lp.x, lp.y, lp.z);
		lp.lp += transNodeConstraints(lp.x, lp.y, lp.z);
		lp.lp += utilisationConstraints(lp.x, lp.y, lp.z);
		lp.lp += bounds(lp.x, lp.y, lp.z);
		lp.lp += binaries(lp.x, lp.y, lp.z);
		System.out.println(lp.lp);
		

		// write lp string to file(lpFile)
		try {
			FileWriter fw = new FileWriter(lp.lpFile);
			BufferedWriter bw = new BufferedWriter(fw);
			bw.write(lp.lp);
			bw.close();
			fw.close();	
		} catch (IOException e) {
			System.out.println("Could not open FileWriter and/or BufferedWriter\n");
			e.printStackTrace();
			System.exit(1);
		}
		
		String cplex_result;
		// run cplex, which prints returned optimum solution
		// https://stackoverflow.com/questions/180158/how-do-i-time-a-methods-execution-in-java
		long startTime = System.currentTimeMillis();
		cplex_result = cplex(lp.lpFile);
		long endTime = System.currentTimeMillis();
		System.out.println("cplex function call took " + (endTime - startTime) + " ms");
		
		
		
		try {
			FileWriter fw = new FileWriter(lp.lpText);
			BufferedWriter bw = new BufferedWriter(fw);
			bw.write(cplex_result);
			bw.close();
			fw.close();	
		} catch (IOException e) {
			System.out.println("Could not open FileWriter and/or BufferedWriter\n");
			e.printStackTrace();
			System.exit(1);
		}
	}
}                              

