package servlets;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.*;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class DisplayRecordsServlet extends HttpServlet {
    private static final String URL = "jdbc:oracle:thin:@localhost:1521/FREEPDB1";
    private static final String USER = "shoaib";
    private static final String PASS = "system";

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        resp.setContentType("text/html");
        PrintWriter out = resp.getWriter();

        out.println("<html><head><title>Student Records</title></head><body>");
        out.println("<h2>All Student Records (from Oracle DB)</h2>");

        try {
            Class.forName("oracle.jdbc.OracleDriver");
            try (Connection con = DriverManager.getConnection(URL, USER, PASS);
                 Statement st = con.createStatement();
                 ResultSet rs = st.executeQuery("SELECT * FROM students ORDER BY id")) {

                out.println("<table border='1' cellpadding='8'>");
                out.println("<tr><th>ID</th><th>Name</th><th>Branch</th><th>Year</th></tr>");
                while (rs.next()) {
                    out.println("<tr><td>" + rs.getInt("id") + "</td><td>" + rs.getString("name")
                            + "</td><td>" + rs.getString("branch") + "</td><td>" + rs.getInt("year") + "</td></tr>");
                }
                out.println("</table>");
            }
        } catch (Exception e) {
            out.println("<p style='color:red'>Error: " + e.getMessage() + "</p>");
        }
        out.println("<br/><a href='crud'>Go to CRUD page</a>");
        out.println("</body></html>");
    }
}