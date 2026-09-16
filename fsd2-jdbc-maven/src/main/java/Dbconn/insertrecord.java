package Dbconn;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
public class insertrecord {
public static void main(String[] args) {
try
		{
			Class.forName("oracle.jdbc.driver.OracleDriver");
			Connection con=DriverManager.getConnection("jdbc:oracle:thin:@localhost:1521/FREEPDB1","shoaib","system");
			Statement stmt=con.createStatement();
			String sql="INSERT INTO csed values(509,'SHOAIB','cse',3)";
			stmt.executeUpdate(sql);
			if(stmt!=null)
			{
				System.out.println("Record inserted....");
			}
			con.close();
		}
		catch(Exception e)
		{
			System.out.println(e);
		}
	}
}
