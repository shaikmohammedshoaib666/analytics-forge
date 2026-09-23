package servlets;

import java.io.IOException;
import java.sql.*;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class RegisterServlet extends HttpServlet {
    private static final String URL = "jdbc:oracle:thin:@localhost:1521/FREEPDB1";
    private static final String USER = "shoaib";
    private static final String PASS = "system";

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        req.getRequestDispatcher("/jsp/register.jsp").forward(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        int id = Integer.parseInt(req.getParameter("id"));
        String name = req.getParameter("name");
        String branch = req.getParameter("branch");
        int year = Integer.parseInt(req.getParameter("year"));

        try {
            Class.forName("oracle.jdbc.OracleDriver");
            try (Connection con = DriverManager.getConnection(URL, USER, PASS);
                 PreparedStatement ps = con.prepareStatement("INSERT INTO students VALUES(?,?,?,?)")) {
                ps.setInt(1, id);
                ps.setString(2, name);
                ps.setString(3, branch);
                ps.setInt(4, year);
                ps.executeUpdate();
                req.setAttribute("message", "Student '" + name + "' registered successfully!");
            }
        } catch (Exception e) {
            req.setAttribute("message", "Error: " + e.getMessage());
        }
        req.getRequestDispatcher("/jsp/register.jsp").forward(req, resp);
    }
}