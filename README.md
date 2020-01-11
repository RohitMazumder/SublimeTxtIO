# SublimeTxtIO
A Sublime Text 3 plugin to ease File Handling !

### Requirements ###
  1. Sublime Text 3
  2. Platform: Windows
  3. Languages supported: Java, Python

### Installation ###
  1. Open Sublime Text, go to Preferences, and click Browse Packages
  2. Download and extract this repository in the directory above.
  3. Restart Sublime Text.
  
### Usage ###
  1. Place the input file in the same directory as your program.
  2. Open the program in Sublime Text, and click the 'TextIO' option from the menu bar.
  3. The output will be obtained in a file named 'output.txt' in the same directory.
  
### Example ###

Directory structure(Before execution):   
Root  
|---HelloWorld.java  
|---input.txt  

__input.txt__
~~~
2
foo
bar
~~~

__HelloWorld.java__
~~~java
import java.util.Scanner;
class HelloWorld
{
	public static void main(String args[])
	{
		Scanner sc=new Scanner(System.in);
		int n = sc.nextInt();
		for(int i=1; i<=n; i++)
		{
			String s = sc.next();
			System.out.println(s);
		}
	}
}
~~~
After Execution:
Root  
|---HelloWorld.class  
|---HelloWorld.java  
|---input.txt  
|---output.txt  

__output.txt__
~~~
foo
bar
~~~
  
  
