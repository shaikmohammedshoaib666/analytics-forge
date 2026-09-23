package servlets;

import beans.UserBean;
import java.io.IOException;
import java.sql.*;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

public class MvcLoginServlet extends HttpServlet {
    private static final String URL = "jdbc:oracle:thin:@localhost:1521/FREEPDB1";
    private static final String USER = "shoaib";
    private static final String PASS = "system";

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        String username = req.getParameter("username");
        String password = req.getParameter("password");

        UserBean user = new UserBean();
        user.setUsername(username);
        user.setPassword(password);

        try {
            Class.forName("oracle.jdbc.OracleDriver");
            try (Connection con = DriverManager.getConnection(URL, USER, PASS);
                 PreparedStatement ps = con.prepareStatement("SELECT role FROM users WHERE username=? AND password=?")) {
                ps.setString(1, username);
                ps.setString(2, password);
                try (ResultSet rs = ps.executeQuery()) {
                    if (rs.next()) {
                        user.setRole(rs.getString("role"));
                        user.setValid(true);
                        HttpSession session = req.getSession();
                        session.setAttribute("user", user);
                        session.setAttribute("username", username);
                        session.setAttribute("role", user.getRole());
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        req.setAttribute("user", user);
        if (user.isValid()) {
            req.getRequestDispatcher("/jsp/mvc-success.jsp").forward(req, resp);
        } else {
            req.getRequestDispatcher("/jsp/mvc-fail.jsp").forward(req, resp);
        }
    }
}