package Dbconn;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
public class deleterecord {
public static void main(String[] args) {
		try
		{
			Class.forName("oracle.jdbc.driver.OracleDriver");
			Connection con=DriverManager.getConnection("jdbc:oracle:thin:@localhost:1521/FREEPDB1","shoaib","system");
			Statement stmt=con.createStatement();
			String sql = "DELETE FROM csed where regno=501";
			stmt.executeUpdate(sql);
			if(stmt!=null)
			{
				System.out.println("Record deleted....");
			}
			con.close();
		}
		catch(Exception e)
		{
			System.out.println(e);
		}
	}
}
