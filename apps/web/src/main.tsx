// Это точка входа frontend-приложения.
// Проще говоря: именно отсюда React начинает рисовать интерфейс в браузере.

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./app/App";
import "./styles/global.css";
import { logoImage } from "./shared/assets";

const favicon = document.querySelector<HTMLLinkElement>("link[rel='icon']") ?? document.createElement("link");
favicon.rel = "icon";
favicon.href = logoImage;
document.head.appendChild(favicon);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
