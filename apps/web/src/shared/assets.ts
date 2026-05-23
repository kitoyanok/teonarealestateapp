// Этот файл хранит пути к картинкам и логотипам.
// Проще говоря: он нужен, чтобы не писать один и тот же путь к изображению в разных компонентах.

export const logoImage = new URL("../../../../views/logo.png", import.meta.url).href;
export const loginPhoto = new URL("../../../../views/photo_1.png", import.meta.url).href;
