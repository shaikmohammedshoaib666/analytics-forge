# FSD2 JDBC Maven (IntelliJ IDEA)

Open this folder in IntelliJ: **File → Open → `fsd2-jdbc-maven`**.

Maven downloads JDBC drivers from `pom.xml`. Click the Maven reload icon after opening.

## Run
Right-click a class in `src/main/java/Dbconn` → Run.

| Class | Database |
|-------|----------|
| `sample` | none (prints welcome) |
| `dbconnection` / `OracleConnect` | Oracle |
| `dbconnection_mysql` | MySQL |
| `insertrecord`, `multipleinsertions`, `update`, `deleterecord`, `fetchdata`, `fetch1`, `dynamic` | Oracle table `csed` |
| `StudentCRUD` | Oracle table `students` |

## Credentials
Oracle: `shoaib` / `system` — `jdbc:oracle:thin:@localhost:1521/FREEPDB1`  
MySQL: `shoaib` / `system` — `jdbc:mysql://localhost:3306/fsd2db`
