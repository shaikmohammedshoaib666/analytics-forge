package Dbconn;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
public class multipleinsertions {
public static void main(String[] args) {
		try
		{
			Class.forName("oracle.jdbc.driver.OracleDriver");
			Connection con=DriverManager.getConnection("jdbc:oracle:thin:@localhost:1521/FREEPDB1","shoaib","system");
			Statement stmt=con.createStatement();
			String insert1 = "INSERT INTO csed VALUES(601,'ALI','cse',3)";
			String insert2 = "INSERT INTO csed VALUES(602,'AHMED','ece',3)";
			String insert3 = "INSERT INTO csed VALUES(603,'RAHUL','cse',3)";
			stmt.addBatch(insert1);
			stmt.addBatch(insert2);
			stmt.addBatch(insert3);
			stmt.executeBatch();
			if(stmt!=null)
			{
				System.out.println("Multiple Records inserted....");
			}
			con.close();
		}
		catch(Exception e)
		{
			System.out.println(e);
		}
}
}
