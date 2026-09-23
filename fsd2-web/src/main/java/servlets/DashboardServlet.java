package servlets;

import java.io.IOException;
import java.io.PrintWriter;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

public class DashboardServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        HttpSession session = req.getSession(false);
        resp.setContentType("text/html");
        PrintWriter out = resp.getWriter();

        if (session == null || session.getAttribute("username") == null) {
            out.println("<html><body>");
            out.println("<h2 style='color:red'>Access Denied</h2>");
            out.println("<p>You must login first.</p>");
            out.println("<a href='login.html'>Login</a>");
            out.println("</body></html>");
            return;
        }

        String username = (String) session.getAttribute("username");
        String role = (String) session.getAttribute("role");
        boolean isAdmin = "admin".equals(role);

        out.println("<html><head><title>Dashboard</title>");
        out.println("<style>body{font-family:Arial;margin:40px;background:#f5f5f5}");
        out.println(".card{background:white;padding:30px;border-radius:8px;max-width:600px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}");
        out.println("a{color:#3498db;text-decoration:none} li{margin:10px 0}</style></head><body>");
        out.println("<div class='card'>");
        out.println("<h2>Dashboard</h2>");
        out.println("<p>Logged in as: <b>" + username + "</b> | Role: " + role + "</p>");
        out.println("<hr/><h3>Menu:</h3><ul>");
        out.println("<li><a href='records'>View Student Records</a></li>");
        out.println("<li><a href='insert-student'>Insert New Student</a></li>");
        out.println("<li><a href='crud'>CRUD Operations</a></li>");
        out.println("<li><a href='submit-feedback'>Submit Feedback</a></li>");

        if (isAdmin) {
            out.println("<li><a href='admin-feedback'><b>View All Feedback (Admin)</b></a></li>");
        }

        out.println("</ul><br/><a href='logout'>Logout</a>");
        out.println("</div></body></html>");
    }
}