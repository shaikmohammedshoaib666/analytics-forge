<%@ page contentType="text/html;charset=UTF-8" %>
<html>
<head><title>JavaBean Form</title></head>
<body>
<h2>Student Form (JavaBean Demo)</h2>
<form method="post" action="jsp/bean-result.jsp">
    ID: <input type="number" name="id" required/><br/><br/>
    Name: <input type="text" name="name" required/><br/><br/>
    Branch: <input type="text" name="branch" required/><br/><br/>
    Year: <input type="number" name="year" required/><br/><br/>
    <input type="submit" value="Submit"/>
</form>
</body>
</html>