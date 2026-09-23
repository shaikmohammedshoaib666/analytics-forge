package servlets;

import beans.FeedbackBean;
import java.io.IOException;
import java.sql.*;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

public class FeedbackServlet extends HttpServlet {
    private static final String URL = "jdbc:oracle:thin:@localhost:1521/FREEPDB1";
    private static final String USER = "shoaib";
    private static final String PASS = "system";

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        HttpSession session = req.getSession(false);
        if (session == null || session.getAttribute("username") == null) {
            resp.sendRedirect("login.html");
            return;
        }
        req.getRequestDispatcher("/jsp/feedback-form.jsp").forward(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        HttpSession session = req.getSession(false);
        if (session == null || session.getAttribute("username") == null) {
            resp.sendRedirect("login.html");
            return;
        }

        FeedbackBean fb = new FeedbackBean();
        fb.setStudentName(req.getParameter("studentName"));
        fb.setRollNo(req.getParameter("rollNo"));
        fb.setCourse(req.getParameter("course"));
        fb.setFeedbackText(req.getParameter("feedbackText"));

        try {
            Class.forName("oracle.jdbc.OracleDriver");
            try (Connection con = DriverManager.getConnection(URL, USER, PASS);
                 PreparedStatement ps = con.prepareStatement(
                         "INSERT INTO feedback (student_name, roll_no, course, feedback_text) VALUES (?,?,?,?)")) {
                ps.setString(1, fb.getStudentName());
                ps.setString(2, fb.getRollNo());
                ps.setString(3, fb.getCourse());
                ps.setString(4, fb.getFeedbackText());
                ps.executeUpdate();
                req.setAttribute("message", "Feedback submitted successfully!");
            }
        } catch (Exception e) {
            req.setAttribute("message", "Error: " + e.getMessage());
        }
        req.getRequestDispatcher("/jsp/feedback-form.jsp").forward(req, resp);
    }
}