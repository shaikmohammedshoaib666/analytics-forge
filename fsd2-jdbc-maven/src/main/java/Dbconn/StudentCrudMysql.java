package Dbconn;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;

public class StudentCrudMysql {
    public static void main(String[] args) {
        try {
            Class.forName(DbConfig.MYSQL_DRIVER);
            try (Connection con = DriverManager.getConnection(
                    DbConfig.MYSQL_URL, DbConfig.MYSQL_USER, DbConfig.MYSQL_PASS)) {

                try (Statement st = con.createStatement()) {
                    st.executeUpdate("DELETE FROM students WHERE id = 99");
                    st.executeUpdate(
                            "INSERT INTO students (id, name, branch, year) VALUES (99, 'Demo', 'CSE', 2)"
                                    + " ON DUPLICATE KEY UPDATE name='Demo', branch='CSE', year=2");
                }

                try (PreparedStatement ps = con.prepareStatement(
                        "UPDATE students SET branch = ? WHERE id = ?")) {
                    ps.setString(1, "AI&DS");
                    ps.setInt(2, 99);
                    ps.executeUpdate();
                }

                System.out.println("--- Students (MySQL) ---");
                try (Statement st = con.createStatement();
                     ResultSet rs = st.executeQuery("SELECT id, name, branch, year FROM students ORDER BY id")) {
                    while (rs.next()) {
                        System.out.println(rs.getInt("id") + " | "
                                + rs.getString("name") + " | "
                                + rs.getString("branch") + " | "
                                + rs.getInt("year"));
                    }
                }

                try (PreparedStatement ps = con.prepareStatement("DELETE FROM students WHERE id = ?")) {
                    ps.setInt(1, 99);
                    ps.executeUpdate();
                }
                System.out.println("CRUD demo finished on MySQL.");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
