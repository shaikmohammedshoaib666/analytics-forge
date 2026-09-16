package Dbconn;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class fetchdata {

    public static void main(String[] args) {

        try {

            Class.forName("oracle.jdbc.driver.OracleDriver");

            Connection con = DriverManager.getConnection(
                    "jdbc:oracle:thin:@localhost:1521/FREEPDB1",
                    "shoaib",
                    "system"
            );

            Statement stmt = con.createStatement();

            String sql = "SELECT * FROM csed";

            ResultSet rs = stmt.executeQuery(sql);

            System.out.println("Student Records:");

            while (rs.next()) {

                System.out.println(
                        rs.getInt("REGNO") + " " +
                                rs.getString("NAME") + " " +
                                rs.getString("BRANCH") + " " +
                                rs.getInt("YR")
                );
            }

            con.close();

        } catch (Exception e) {
            System.out.println(e);
        }
    }
}
