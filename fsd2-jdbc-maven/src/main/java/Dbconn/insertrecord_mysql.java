package Dbconn;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

public class insertrecord_mysql {
    public static void main(String[] args) {
        try {
            Class.forName(DbConfig.MYSQL_DRIVER);
            Connection con = DriverManager.getConnection(
                    DbConfig.MYSQL_URL, DbConfig.MYSQL_USER, DbConfig.MYSQL_PASS);
            Statement stmt = con.createStatement();
            String sql = "INSERT INTO csed VALUES(504,'shoaib','cse',3)";
            stmt.executeUpdate(sql);
            System.out.println("Record inserted....");
            con.close();
        } catch (Exception e) {
            System.out.println(e);
        }
    }
}
