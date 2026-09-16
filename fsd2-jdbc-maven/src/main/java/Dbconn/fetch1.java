package Dbconn;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Scanner;

public class fetch1 {

    public static void main(String[] args) {

        try {

            Scanner sc = new Scanner(System.in);

            System.out.println("Enter Registration No:");
            int rno = sc.nextInt();

            System.out.println("Enter Student Name:");
            String name = sc.next();

            Class.forName("oracle.jdbc.driver.OracleDriver");

            Connection con = DriverManager.getConnection(
                    "jdbc:oracle:thin:@localhost:1521/FREEPDB1",
                    "shoaib",
                    "system"
            );

            PreparedStatement pst = con.prepareStatement(
                    "SELECT * FROM csed WHERE regno=? AND name=?"
            );

            pst.setInt(1, rno);
            pst.setString(2, name);

            ResultSet rs = pst.executeQuery();

            if (rs.next()) {

                System.out.println(
                        "Student Found: " +
                                rs.getInt("REGNO") + " " +
                                rs.getString("NAME") + " " +
                                rs.getString("BRANCH") + " " +
                                rs.getInt("YR")
                );

            } else {

                System.out.println("Not a student");

            }

            con.close();
            sc.close();

        } catch (Exception e) {

            System.out.println(e);

        }
    }
}
