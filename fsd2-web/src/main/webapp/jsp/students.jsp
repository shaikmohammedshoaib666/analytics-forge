<%@ page contentType="text/html;charset=UTF-8" %>
<%@ page import="java.sql.*" %>
<html>
<head><title>Student Records (JSP)</title></head>
<body>
<h2>Student Records from Database</h2>
<table border="1" cellpadding="8">
    <tr><th>ID</th><th>Name</th><th>Branch</th><th>Year</th></tr>
<%
    Class.forName("oracle.jdbc.OracleDriver");
    Connection con = DriverManager.getConnection("jdbc:oracle:thin:@localhost:1521/FREEPDB1", "shoaib", "system");
    Statement st = con.createStatement();
    ResultSet rs = st.executeQuery("SELECT * FROM students ORDER BY id");
    while (rs.next()) {
%>
    <tr>
        <td><%= rs.getInt("id") %></td>
        <td><%= rs.getString("name") %></td>
        <td><%= rs.getString("branch") %></td>
        <td><%= rs.getInt("year") %></td>
    </tr>
<%
    }
    rs.close();
    st.close();
    con.close();
%>
</table>
<br/><a href="../index.html">Home</a>
</body>
</html>