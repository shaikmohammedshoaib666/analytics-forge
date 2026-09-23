package Dbconn;
import java.sql.Connection;
import java.sql.DriverManager;
public class dbconnection_mysql {
    public static void main(String[] args) {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            Connection con = DriverManager.getConnection(
                "jdbc:mysql://localhost:3306/fsd2db?useSSL=false&allowPublicKeyRetrieval=true",
                "shoaib", "system");
            if (con != null) System.out.println("MySQL database connected");
            con.close();
        } catch (Exception e) { System.out.println(e); }
    }
}
