package servlets;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.*;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class CrudServlet extends HttpServlet {
    private static final String URL = "jdbc:oracle:thin:@localhost:1521/FREEPDB1";
    private static final String USER = "shoaib";
    private static final String PASS = "system";

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        String action = req.getParameter("action");
        if (action == null) action = "list";

        resp.setContentType("text/html");
        PrintWriter out = resp.getWriter();
        out.println("<html><head><title>CRUD Operations</title></head><body>");
        out.println("<h2>Student CRUD Operations</h2>");

        try {
            Class.forName("oracle.jdbc.OracleDriver");
            try (Connection con = DriverManager.getConnection(URL, USER, PASS)) {
                switch (action) {
                    case "delete":
                        int delId = Integer.parseInt(req.getParameter("id"));
                        try (PreparedStatement ps = con.prepareStatement("DELETE FROM students WHERE id=?")) {
                            ps.setInt(1, delId);
                            ps.executeUpdate();
                        }
                        out.println("<p style='color:green'>Deleted student id=" + delId + "</p>");
                        break;
                }
                // Always show all records
                out.println("<table border='1' cellpadding='8'><tr><th>ID</th><th>Name</th><th>Branch</th><th>Year</th><th>Action</th></tr>");
                try (Statement st = con.createStatement();
                     ResultSet rs = st.executeQuery("SELECT * FROM students ORDER BY id")) {
                    while (rs.next()) {
                        out.println("<tr><td>" + rs.getInt("id") + "</td><td>" + rs.getString("name")
                                + "</td><td>" + rs.getString("branch") + "</td><td>" + rs.getInt("year")
                                + "</td><td><a href='crud?action=delete&id=" + rs.getInt("id") + "'>Delete</a></td></tr>");
                    }
                }
                out.println("</table>");
            }
        } catch (Exception e) {
            out.println("<p style='color:red'>Error: " + e.getMessage() + "</p>");
        }

        out.println("<h3>Insert New Student</h3>");
        out.println("<form method='post' action='crud'>");
        out.println("ID: <input name='id' type='number'/><br/><br/>");
        out.println("Name: <input name='name'/><br/><br/>");
        out.println("Branch: <input name='branch'/><br/><br/>");
        out.println("Year: <input name='year' type='number'/><br/><br/>");
        out.println("<input type='submit' value='Insert'/></form>");

        out.println("<h3>Update Student Branch</h3>");
        out.println("<form method='post' action='crud'>");
        out.println("<input type='hidden' name='action' value='update'/>");
        out.println("Student ID: <input name='id' type='number'/><br/><br/>");
        out.println("New Branch: <input name='branch'/><br/><br/>");
        out.println("<input type='submit' value='Update'/></form>");
        out.println("</body></html>");
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        String action = req.getParameter("action");

        try {
            Class.forName("oracle.jdbc.OracleDriver");
            try (Connection con = DriverManager.getConnection(URL, USER, PASS)) {
                if ("update".equals(action)) {
                    int id = Integer.parseInt(req.getParameter("id"));
                    String branch = req.getParameter("branch");
                    try (PreparedStatement ps = con.prepareStatement("UPDATE students SET branch=? WHERE id=?")) {
                        ps.setString(1, branch);
                        ps.setInt(2, id);
                        ps.executeUpdate();
                    }
                } else {
                    int id = Integer.parseInt(req.getParameter("id"));
                    String name = req.getParameter("name");
                    String branch = req.getParameter("branch");
                    int year = Integer.parseInt(req.getParameter("year"));
                    try (PreparedStatement ps = con.prepareStatement("INSERT INTO students VALUES(?,?,?,?)")) {
                        ps.setInt(1, id);
                        ps.setString(2, name);
                        ps.setString(3, branch);
                        ps.setInt(4, year);
                        ps.executeUpdate();
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        resp.sendRedirect("crud");
    }
}