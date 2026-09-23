<%@ page contentType="text/html;charset=UTF-8" %>
<%
    HttpSession ses = request.getSession(false);
    if (ses == null || ses.getAttribute("username") == null) {
        response.sendRedirect("../login.html");
        return;
    }
    String username = (String) ses.getAttribute("username");
    String msg = (String) request.getAttribute("message");
%>
<html>
<head><title>Submit Feedback</title>
<style>
    body { font-family: Arial; margin: 40px; background: #f5f5f5; }
    .container { background: white; padding: 30px; border-radius: 8px; max-width: 500px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    h2 { color: #2c3e50; }
    input, textarea, select { width: 100%; padding: 8px; margin: 5px 0 15px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
    textarea { height: 120px; resize: vertical; }
    input[type="submit"] { background: #3498db; color: white; border: none; cursor: pointer; font-size: 16px; }
    input[type="submit"]:hover { background: #2980b9; }
    .success { color: green; font-weight: bold; }
    .nav { margin-bottom: 20px; }
    .nav a { margin-right: 15px; color: #3498db; text-decoration: none; }
</style>
</head>
<body>
<div class="nav">
    <a href="../dashboard">Dashboard</a>
    <a href="../logout">Logout (<%= username %>)</a>
</div>
<div class="container">
    <h2>Submit Feedback</h2>
    <% if (msg != null) { %>
        <p class="success"><%= msg %></p>
    <% } %>
    <form method="post" action="../submit-feedback">
        <label>Student Name:</label>
        <input type="text" name="studentName" required/>

        <label>Roll No:</label>
        <input type="text" name="rollNo" required/>

        <label>Course:</label>
        <select name="course">
            <option value="FSD">Full Stack Development</option>
            <option value="DBMS">Database Management</option>
            <option value="OS">Operating Systems</option>
            <option value="CN">Computer Networks</option>
            <option value="AI">Artificial Intelligence</option>
        </select>

        <label>Feedback:</label>
        <textarea name="feedbackText" placeholder="Write your feedback here..." required></textarea>

        <input type="submit" value="Submit Feedback"/>
    </form>
</div>
</body>
</html>