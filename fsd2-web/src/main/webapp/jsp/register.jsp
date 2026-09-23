<%@ page contentType="text/html;charset=UTF-8" %>
<html>
<head><title>Student Registration</title></head>
<body>
<h2>Student Registration</h2>
<%
    String msg = (String) request.getAttribute("message");
    if (msg != null) {
%>
<p style="color:green; font-weight:bold"><%= msg %></p>
<%  } %>
<form method="post" action="../register">
    ID: <input type="number" name="id" required/><br/><br/>
    Name: <input type="text" name="name" required/><br/><br/>
    Branch: <input type="text" name="branch" required/><br/><br/>
    Year: <input type="number" name="year" min="1" max="4" required/><br/><br/>
    <input type="submit" value="Register"/>
</form>
<br/><a href="../records">View All Students</a>
</body>
</html>