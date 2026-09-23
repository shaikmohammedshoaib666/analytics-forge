<%@ page contentType="text/html;charset=UTF-8" %>
<html>
<head><title>JSP Calculator</title></head>
<body>
<h2>Simple Calculator (JSP)</h2>
<form method="post" action="jsp/calculator.jsp">
    Number 1: <input type="number" name="num1" step="any" value="<%= request.getParameter("num1") != null ? request.getParameter("num1") : "" %>"/><br/><br/>
    Number 2: <input type="number" name="num2" step="any" value="<%= request.getParameter("num2") != null ? request.getParameter("num2") : "" %>"/><br/><br/>
    Operation:
    <select name="op">
        <option value="+">+</option>
        <option value="-">-</option>
        <option value="*">×</option>
        <option value="/">÷</option>
    </select><br/><br/>
    <input type="submit" value="Calculate"/>
</form>

<%
    String n1 = request.getParameter("num1");
    String n2 = request.getParameter("num2");
    String op = request.getParameter("op");
    if (n1 != null && n2 != null && op != null) {
        double a = Double.parseDouble(n1);
        double b = Double.parseDouble(n2);
        double result = 0;
        switch (op) {
            case "+": result = a + b; break;
            case "-": result = a - b; break;
            case "*": result = a * b; break;
            case "/": result = (b != 0) ? a / b : 0; break;
        }
%>
<h3>Result: <%= n1 %> <%= op %> <%= n2 %> = <%= result %></h3>
<%
    }
%>
</body>
</html>