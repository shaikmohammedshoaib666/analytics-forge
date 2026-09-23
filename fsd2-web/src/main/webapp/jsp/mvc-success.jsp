<%@ page contentType="text/html;charset=UTF-8" %>
<jsp:useBean id="user" class="beans.UserBean" scope="request"/>
<html>
<head><title>Login Success</title></head>
<body>
<h2 style="color:green">Welcome, <jsp:getProperty name="user" property="username"/>!</h2>
<p>Role: <jsp:getProperty name="user" property="role"/></p>
<p>Session ID: <%= session.getId() %></p>
<a href="../dashboard">Dashboard</a> | <a href="../logout">Logout</a>
</body>
</html>