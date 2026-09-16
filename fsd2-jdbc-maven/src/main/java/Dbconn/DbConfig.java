package Dbconn;

public final class DbConfig {
    private DbConfig() {}

    public static final String MYSQL_URL =
            "jdbc:mysql://localhost:3306/fsd2db?useSSL=false&allowPublicKeyRetrieval=true";
    public static final String MYSQL_USER = "shoaib";
    public static final String MYSQL_PASS = "system";
    public static final String MYSQL_DRIVER = "com.mysql.cj.jdbc.Driver";

    public static final String ORACLE_URL = "jdbc:oracle:thin:@localhost:1521/FREEPDB1";
    public static final String ORACLE_USER = "shoaib";
    public static final String ORACLE_PASS = "system";
    public static final String ORACLE_DRIVER = "oracle.jdbc.OracleDriver";
}
