# FSD2 JDBC Maven (IntelliJ IDEA)

All old `fsd2-jdbc` IntelliJ programs live here under `src/main/java/Dbconn`.
Drivers are in `pom.xml` (no manual jar files).

Servlet + JSP + login `doPost` labs are in `../fsd2-web` (Tomcat 9 + SmartTomcat, not this console project).

## Open in IntelliJ
1. File → Open → this `fsd2-jdbc-maven` folder
2. Trust the project
3. Maven tool window → Reload
4. Expand `src/main/java/Dbconn` → open a class → green ▶ Run

If this folder is not yet on your Mac, copy it to:

`~/IdeaProjects/fsd2-jdbc-maven`

## Programs
| Class | What it does |
|-------|----------------|
| `sample` | Prints welcome |
| `OracleConnect` | Test Oracle |
| `dbconnection` | Connect Oracle |
| `dbconnection_mysql` | Connect MySQL |
| `insertrecord` | Insert into Oracle `csed` |
| `insertrecord_mysql` | Insert into MySQL `csed` |
| `multipleinsertions` | Batch insert (Oracle) |
| `update` | Update row (Oracle) |
| `deleterecord` | Delete row (Oracle) |
| `fetchdata` | Select all `csed` |
| `fetch1` | Select by regno + name |
| `dynamic` | PreparedStatement insert from keyboard |
| `StudentCRUD` | Full CRUD (Oracle `students`) |
| `StudentCrudMysql` | CRUD (MySQL `students`) |
| `DbConfig` | Shared URLs / passwords |

## Credentials
- Oracle: `shoaib` / `system` — `jdbc:oracle:thin:@localhost:1521/FREEPDB1`
- MySQL: `shoaib` / `system` — `jdbc:mysql://localhost:3306/fsd2db`
