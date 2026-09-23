# FSD2 web labs (Servlets + JSP + JDBC)

Tomcat 9 runs this app. **Official Tomcat in IntelliJ needs Ultimate.** Use **SmartTomcat** (free) or `run-tomcat.sh`.

Do **not** enable the **Jakarta EE** / **Tomcat and TomEE** plugins unless Ultimate is active. They stay locked on Community / expired trial. This project uses **`javax.servlet`** (Java EE 8), which matches **Tomcat 9.0.120**. Jakarta Servlet (`jakarta.servlet`) needs Tomcat 10+.

## Install SmartTomcat in IntelliJ

1. **IntelliJ IDEA → Settings → Plugins → Marketplace**
2. Search **SmartTomcat** (author **zengkid**) → **Install** → **Restart IDE**
3. **File → Open** this `fsd2-web` folder (Maven). Trust + reload Maven.
4. **Run → Edit Configurations**
   - Delete any red **FSD2 Tomcat** row (`Unknown run configuration type`)
   - If **FSD2 SmartTomcat** is missing: **+ → SmartTomcat**
5. Confirm:

| Field | Value |
|--------|--------|
| Name | `FSD2 SmartTomcat` |
| Tomcat Server | `/Users/sk.md.shoaib.raza/Tools/apache-tomcat-9.0.120` |
| Deployment / Webapp | `src/main/webapp` (not `target/` and not `out/`) |
| Context path | `/fsd2_web` |
| HTTP port | `8080` |

6. Terminal: `docker start oracle-xe`
7. Top dropdown → **FSD2 SmartTomcat** → green ▶
8. Browser: [http://localhost:8080/fsd2_web/login.html](http://localhost:8080/fsd2_web/login.html)
   - Student: `shoaib` / `system`
   - Admin: `admin` / `admin123`

That runs `LoginServlet.doPost()`. There is no ▶ on the servlet file itself (no `main()`).

If **+** has no SmartTomcat: **Plugins → Installed** → SmartTomcat checkbox on → restart.

## Copy onto the Mac

```bash
chmod +x copy-to-intellij.sh
./copy-to-intellij.sh ~/Projects/fsd2-web
```

## No plugin (command line)

```bash
docker start oracle-xe
chmod +x run-tomcat.sh
./run-tomcat.sh
```

## Seed Oracle tables

```bash
docker exec -i oracle-xe sqlplus -s shoaib/system@//localhost/FREEPDB1 < sql/init-oracle.sql
```

## Lab map

| URL | Class | Notes |
|-----|--------|--------|
| `/hello` | `HelloServlet` | Smoke test |
| `/login.html` → POST `/login` | `LoginServlet` | Assignment: `doPost` login |
| `/crud` | `CrudServlet` | JDBC CRUD |
| `/records` | `DisplayRecordsServlet` | List students |
| `/insert-student` | `InsertStudentServlet` | PreparedStatement |
| `/dashboard` `/logout` | session labs | After login |
| `/jsp/calculator.jsp` | JSP | Unit 2 |
| `/jsp/mvc-login.jsp` | `MvcLoginServlet` | MVC |
| `/register` | `RegisterServlet` | Registration |
| `/submit-feedback` | `FeedbackServlet` | Mini project |

## Credentials

- Oracle: `shoaib` / `system` — `jdbc:oracle:thin:@localhost:1521/FREEPDB1`
- Tomcat Manager (optional): `admin` / `admin`

Console JDBC programs stay in `../fsd2-jdbc-maven`.
