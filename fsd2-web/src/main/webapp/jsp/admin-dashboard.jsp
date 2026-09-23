<%@ page contentType="text/html;charset=UTF-8" %>
<%@ page import="java.sql.*, java.util.*" %>
<%
    HttpSession ses = request.getSession(false);
    if (ses == null || !"admin".equals(ses.getAttribute("role"))) {
        response.sendRedirect("../login.html");
        return;
    }
    String username = (String) ses.getAttribute("username");
%>
<html>
<head><title>Admin - View Feedback</title>
<style>
    body { font-family: Arial; margin: 40px; background: #f5f5f5; }
    .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    h2 { color: #2c3e50; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th { background: #3498db; color: white; padding: 10px; text-align: left; }
    td { padding: 10px; border-bottom: 1px solid #ddd; }
    tr:hover { background: #f0f0f0; }
    .nav { margin-bottom: 20px; }
    .nav a { margin-right: 15px; color: #3498db; text-decoration: none; }
    .count { color: #777; font-size: 14px; }
</style>
</head>
<body>
<div class="nav">
    <a href="../dashboard">Dashboard</a>
    <a href="../logout">Logout (<%= username %>)</a>
</div>
<div class="container">
    <h2>All Student Feedback</h2>
<%
    int count = 0;
    Class.forName("oracle.jdbc.OracleDriver");
    Connection con = DriverManager.getConnection("jdbc:oracle:thin:@localhost:1521/FREEPDB1", "shoaib", "system");
    PreparedStatement ps = con.prepareStatement("SELECT * FROM feedback ORDER BY submitted_at DESC");
    ResultSet rs = ps.executeQuery();
%>
    <table>
        <tr><th>#</th><th>Student</th><th>Roll No</th><th>Course</th><th>Feedback</th><th>Date</th></tr>
<%
    while (rs.next()) {
        count++;
%>
        <tr>
            <td><%= rs.getInt("id") %></td>
            <td><%= rs.getString("student_name") %></td>
            <td><%= rs.getString("roll_no") %></td>
            <td><%= rs.getString("course") %></td>
            <td><%= rs.getString("feedback_text") %></td>
            <td><%= rs.getTimestamp("submitted_at") %></td>
        </tr>
<%
    }
    rs.close(); ps.close(); con.close();
%>
    </table>
    <p class="count">Total feedback entries: <%= count %></p>
</div>
</body>
</html>