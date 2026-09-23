package Dbconn;
import java.sql.Connection;
import java.sql.DriverManager;
public class dbconnection {
public static void main(String[] args) {
		try
		{
			Class.forName("oracle.jdbc.driver.OracleDriver");
			Connection con=DriverManager.getConnection("jdbc:oracle:thin:@localhost:1521/FREEPDB1","shoaib","system");
			if(con!=null)
			{
				System.out.println("oracle database connected");
			}
			con.close();
		}
		catch(Exception e)
		{
			System.out.println(e);
}
}
}
