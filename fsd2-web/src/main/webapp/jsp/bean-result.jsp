<%@ page contentType="text/html;charset=UTF-8" %>
<jsp:useBean id="student" class="beans.StudentBean" scope="request"/>
<jsp:setProperty name="student" property="*"/>
<html>
<head><title>Bean Result</title></head>
<body>
<h2>Student Data (from JavaBean)</h2>
<table border="1" cellpadding="8">
    <tr><th>Field</th><th>Value</th></tr>
    <tr><td>ID</td><td><jsp:getProperty name="student" property="id"/></td></tr>
    <tr><td>Name</td><td><jsp:getProperty name="student" property="name"/></td></tr>
    <tr><td>Branch</td><td><jsp:getProperty name="student" property="branch"/></td></tr>
    <tr><td>Year</td><td><jsp:getProperty name="student" property="year"/></td></tr>
</table>
<br/><a href="bean-form.jsp">Back</a>
</body>
</html>