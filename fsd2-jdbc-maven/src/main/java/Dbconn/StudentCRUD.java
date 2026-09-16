package Dbconn;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;

/**
 * Simple JDBC CRUD demo for FSD2 (students table).
 */
public class StudentCRUD {
    private static final String URL =
            "jdbc:oracle:thin:@localhost:1521/FREEPDB1";
    private static final String USER = "shoaib";
    private static final String PASSWORD = "system";

    public static void main(String[] args) {
        try {
            Class.forName("oracle.jdbc.OracleDriver");

            try (Connection con = DriverManager.getConnection(URL, USER, PASSWORD)) {
                createTable(con);
                insertStudent(con, 1, "Shoaib", "CSE");
                insertStudent(con, 2, "Aisha", "IT");
                listStudents(con);
                updateStudent(con, 1, "AI&DS");
                listStudents(con);
                deleteStudent(con, 2);
                listStudents(con);
                System.out.println("CRUD demo finished.");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void createTable(Connection con) throws Exception {
        try (Statement st = con.createStatement()) {
            st.executeUpdate(
                    "BEGIN "
                            + "EXECUTE IMMEDIATE 'DROP TABLE students PURGE'; "
                            + "EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; "
                            + "END;");
            st.executeUpdate(
                    "CREATE TABLE students ("
                            + "id NUMBER PRIMARY KEY, "
                            + "name VARCHAR2(50) NOT NULL, "
                            + "branch VARCHAR2(30)"
                            + ")");
            System.out.println("Table STUDENTS created.");
        }
    }

    private static void insertStudent(Connection con, int id, String name, String branch)
            throws Exception {
        String sql = "INSERT INTO students (id, name, branch) VALUES (?, ?, ?)";
        try (PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setInt(1, id);
            ps.setString(2, name);
            ps.setString(3, branch);
            ps.executeUpdate();
            System.out.println("Inserted: " + name);
        }
    }

    private static void listStudents(Connection con) throws Exception {
        System.out.println("--- Students ---");
        try (Statement st = con.createStatement();
             ResultSet rs = st.executeQuery("SELECT id, name, branch FROM students ORDER BY id")) {
            while (rs.next()) {
                System.out.println(
                        rs.getInt("id") + " | "
                                + rs.getString("name") + " | "
                                + rs.getString("branch"));
            }
        }
    }

    private static void updateStudent(Connection con, int id, String branch) throws Exception {
        String sql = "UPDATE students SET branch = ? WHERE id = ?";
        try (PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setString(1, branch);
            ps.setInt(2, id);
            ps.executeUpdate();
            System.out.println("Updated id=" + id + " branch=" + branch);
        }
    }

    private static void deleteStudent(Connection con, int id) throws Exception {
        String sql = "DELETE FROM students WHERE id = ?";
        try (PreparedStatement ps = con.prepareStatement(sql)) {
            ps.setInt(1, id);
            ps.executeUpdate();
            System.out.println("Deleted id=" + id);
        }
    }
}
