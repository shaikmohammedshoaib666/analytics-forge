<%@ page contentType="text/html;charset=UTF-8" %>
<html>
<head><title>MVC Login</title></head>
<body>
<h2>Login (MVC Pattern)</h2>
<form method="post" action="../mvc-login">
    Username: <input type="text" name="username" required/><br/><br/>
    Password: <input type="password" name="password" required/><br/><br/>
    <input type="submit" value="Login"/>
</form>
<p>Test: username=<b>shoaib</b>, password=<b>system</b></p>
</body>
</html>