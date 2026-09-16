package Dbconn;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class OracleConnect {
    private static final String URL =
            "jdbc:oracle:thin:@localhost:1521/FREEPDB1";
    private static final String USER = "shoaib";
    private static final String PASSWORD = "system";

    public static void main(String[] args) {
        System.out.println("Connecting to Oracle...");

        try {
            Class.forName("oracle.jdbc.OracleDriver");

            try (Connection con = DriverManager.getConnection(URL, USER, PASSWORD);
                 Statement st = con.createStatement();
                 ResultSet rs = st.executeQuery(
                         "SELECT user AS username, TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS') AS now_ts FROM dual")) {

                System.out.println("Connected successfully!");

                while (rs.next()) {
                    System.out.println("Logged in as : " + rs.getString("username"));
                    System.out.println("Server time  : " + rs.getString("now_ts"));
                }
            }
        } catch (Exception e) {
            System.err.println("Connection failed:");
            e.printStackTrace();
        }
    }
}
