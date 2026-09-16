package Dbconn;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

public class update {

    public static void main(String[] args) {

        try {
            Class.forName("oracle.jdbc.driver.OracleDriver");

            Connection con = DriverManager.getConnection(
                    "jdbc:oracle:thin:@localhost:1521/FREEPDB1",
                    "shoaib",
                    "system"
            );

            Statement stmt = con.createStatement();

            String sql = "UPDATE csed SET name='lukkuman', branch='ece', year=4 WHERE regno=507";

            stmt.executeUpdate(sql);

            if (stmt != null) {
                System.out.println("Record updated...");
            }

            con.close();

        } catch (Exception e) {
            System.out.println(e);
        }
    }
}
