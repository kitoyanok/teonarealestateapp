// Этот файл хранит заранее подготовленный список риелторов.
// Простыми словами: при первом запуске система сама создает этих сотрудников в базе,
// чтобы можно было сразу войти в приложение и показать работу системы без отдельного экрана администрирования.
export type SeedRealtor = {
  login: string;
  password: string;
  name: string;
  email: string;
  phone: string;
};

export const seedRealtors: SeedRealtor[] = [
  {
    login: "ivan.nikitin",
    password: "Teona2026!",
    name: "Иван Никитин",
    email: "ivan.nikitin@teona.local",
    phone: "+7 (918) 111-11-01"
  },
  {
    login: "kirill.nabiev",
    password: "Teona2026!",
    name: "Кирилл Набиев",
    email: "kirill.nabiev@teona.local",
    phone: "+7 (918) 111-11-02"
  },
  {
    login: "ilya.berezin",
    password: "Teona2026!",
    name: "Илья Березин",
    email: "ilya.berezin@teona.local",
    phone: "+7 (918) 111-11-03"
  },
  {
    login: "marina.nikiforova",
    password: "Teona2026!",
    name: "Марина Никифорова",
    email: "marina.nikiforova@teona.local",
    phone: "+7 (918) 111-11-04"
  },
  {
    login: "nikita.zubach",
    password: "Teona2026!",
    name: "Никита Зубач",
    email: "nikita.zubach@teona.local",
    phone: "+7 (918) 111-11-05"
  }
];
