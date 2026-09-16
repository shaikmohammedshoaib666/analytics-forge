package Dbconn;

import java.sql.*;
import java.util.Scanner;

public class dynamic {

    public static void main(String[] args) {

        try {

            Scanner sc = new Scanner(System.in);

            System.out.print("Enter Student ID: ");
            int id = sc.nextInt();

            System.out.print("Enter Student Name: ");
            String name = sc.next();

            System.out.print("Enter Branch: ");
            String branch = sc.next();

            System.out.print("Enter Year: ");
            int year = sc.nextInt();

            Class.forName("oracle.jdbc.driver.OracleDriver");

            Connection con = DriverManager.getConnection(
                    "jdbc:oracle:thin:@localhost:1521/FREEPDB1",
                    "shoaib",
                    "system"
            );

            String sql = "INSERT INTO csed VALUES (?, ?, ?, ?)";

            PreparedStatement ps = con.prepareStatement(sql);

            ps.setInt(1, id);
            ps.setString(2, name);
            ps.setString(3, branch);
            ps.setInt(4, year);

            int rows = ps.executeUpdate();

            if (rows > 0) {
                System.out.println("Record inserted successfully");
            }

            con.close();
            sc.close();

        } catch (Exception e) {
            System.out.println(e);
        }
    }
}
