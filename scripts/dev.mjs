import { spawn } from "node:child_process";
import net from "node:net";

const webPort = Number(process.env.WEB_PORT ?? 5002);
const apiPort = Number(process.env.API_PORT ?? process.env.NODE_API_PORT ?? 5003);
const searchPort = Number(process.env.PYTHON_SEARCH_PORT ?? 8002);

async function isPortBusy(port) {
  return new Promise((resolve) => {
    const server = net.createServer();

    server.once("error", (error) => {
      if (error && typeof error === "object" && "code" in error && error.code === "EADDRINUSE") {
        resolve(true);
        return;
      }
      resolve(false);
    });

    server.once("listening", () => {
      server.close(() => resolve(false));
    });

    server.listen(port, "0.0.0.0");
  });
}

const busyPorts = [];

if (await isPortBusy(webPort)) {
  busyPorts.push(webPort);
}

if (await isPortBusy(apiPort)) {
  busyPorts.push(apiPort);
}

if (await isPortBusy(searchPort)) {
  busyPorts.push(searchPort);
}

if (busyPorts.length > 0) {
  console.error(
    [
      `EstateFlow dev start aborted: port ${busyPorts.join(", ")} ${busyPorts.length === 1 ? "is" : "are"} already in use.`,
      "Stop the old process first, then run `npm run dev` again.",
      `Expected ports: web=${webPort}, api=${apiPort}, search=${searchPort}.`
    ].join("\n")
  );
  process.exit(1);
}

const npmCommand = process.platform === "win32" ? "npm.cmd" : "npm";

const child = spawn(npmCommand, ["run", "dev:split"], {
  stdio: "inherit",
  env: process.env
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 0);
});
