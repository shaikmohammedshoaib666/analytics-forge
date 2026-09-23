package servlets;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.*;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

public class LoginServlet extends HttpServlet {
    private static final String URL = "jdbc:oracle:thin:@localhost:1521/FREEPDB1";
    private static final String USER = "shoaib";
    private static final String PASS = "system";

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        resp.sendRedirect("login.html");
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        String username = req.getParameter("username");
        String password = req.getParameter("password");

        resp.setContentType("text/html");
        PrintWriter out = resp.getWriter();

        try {
            Class.forName("oracle.jdbc.OracleDriver");
            try (Connection con = DriverManager.getConnection(URL, USER, PASS);
                 PreparedStatement ps = con.prepareStatement(
                         "SELECT username, role FROM users WHERE username=? AND password=?")) {
                ps.setString(1, username);
                ps.setString(2, password);
                try (ResultSet rs = ps.executeQuery()) {
                    if (rs.next()) {
                        HttpSession session = req.getSession();
                        session.setAttribute("username", rs.getString("username"));
                        session.setAttribute("role", rs.getString("role"));
                        out.println("<html><body>");
                        out.println("<h2 style='color:green'>Login Successful!</h2>");
                        out.println("<p>Welcome, <b>" + rs.getString("username") + "</b> (Role: " + rs.getString("role") + ")</p>");
                        out.println("<a href='dashboard'>Go to Dashboard</a> | <a href='logout'>Logout</a>");
                        out.println("</body></html>");
                    } else {
                        out.println("<html><body>");
                        out.println("<h2 style='color:red'>Login Failed!</h2>");
                        out.println("<p>Invalid username or password.</p>");
                        out.println("<a href='login.html'>Try Again</a>");
                        out.println("</body></html>");
                    }
                }
            }
        } catch (Exception e) {
            out.println("<html><body><p style='color:red'>Error: " + e.getMessage() + "</p></body></html>");
        }
    }
}