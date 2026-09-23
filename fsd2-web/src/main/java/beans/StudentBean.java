package beans;

import java.io.Serializable;

public class StudentBean implements Serializable {
    private int id;
    private String name;
    private String branch;
    private int year;

    public StudentBean() {}

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getBranch() { return branch; }
    public void setBranch(String branch) { this.branch = branch; }

    public int getYear() { return year; }
    public void setYear(int year) { this.year = year; }
}