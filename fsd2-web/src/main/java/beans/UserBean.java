package beans;

import java.io.Serializable;

public class UserBean implements Serializable {
    private String username;
    private String password;
    private String role;
    private boolean valid;

    public UserBean() {}

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public boolean isValid() { return valid; }
    public void setValid(boolean valid) { this.valid = valid; }
}