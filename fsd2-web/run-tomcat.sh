#!/bin/bash
# Run the WAR on local Tomcat without any IntelliJ plugin (Community-safe).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CATALINA_HOME="${CATALINA_HOME:-$HOME/Tools/apache-tomcat-9.0.120}"
JAVA_HOME="${JAVA_HOME:-/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home}"
export JAVA_HOME CATALINA_HOME

if [ ! -x "$CATALINA_HOME/bin/startup.sh" ]; then
  echo "Tomcat not found at $CATALINA_HOME"
  exit 1
fi

if ! command -v mvn >/dev/null 2>&1; then
  echo "Maven (mvn) is required to build the WAR"
  exit 1
fi

(cd "$ROOT" && mvn -q -DskipTests package)

WAR="$ROOT/target/fsd2_web.war"
rm -rf "$CATALINA_HOME/webapps/fsd2_web" "$CATALINA_HOME/webapps/fsd2_web.war"
cp "$WAR" "$CATALINA_HOME/webapps/fsd2_web.war"

"$CATALINA_HOME/bin/startup.sh"
echo "Deployed. Open http://localhost:8080/fsd2_web/login.html"
echo "Stop with: $CATALINA_HOME/bin/shutdown.sh"
