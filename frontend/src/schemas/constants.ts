import { type CardData } from "../components/HeroResumeCard";

const CARDS: CardData[] = [
  {
    id: "a",
    name: "Jake Taylor",
    contact: "jake.t@email.com · (555) 123-4567 · linkedin.com/in/jt",
    edu: {
      school: "State University — B.S. Computer Science",
      years: "2018 – 2022",
    },
    exp: [
      {
        title: "Software Engineer · Acme Corp",
        years: "2022 – present",
        bars: ["f", "m", "s"],
      },
      {
        title: "Engineering Intern · StartupCo",
        years: "Summer 2021",
        bars: ["m", "s"],
      },
    ],
    skills: ["Python", "React", "TypeScript", "PostgreSQL", "Docker", "AWS"],
    score: { val: "88 / 100", bg: "#eaf3de", color: "#3b6d11" },
  },
  {
    id: "b",
    name: "Alex Morgan",
    contact: "alex@email.com · (555) 987-6543 · linkedin.com/in/am",
    edu: {
      school: "Tech Institute — M.S. Software Engineering",
      years: "2017 – 2021",
    },
    exp: [
      {
        title: "Senior Developer · MegaCorp",
        years: "2021 – present",
        bars: ["f", "f", "m"],
      },
      {
        title: "Junior Developer · Agency",
        years: "2019 – 2021",
        bars: ["m", "s"],
      },
    ],
    projects: [
      {
        title: "Open Source CLI Tool",
        year: "2022",
        bars: ["m"],
        skills: ["TypeScript", "Go", "Redis"],
      },
    ],
    score: { val: "64 / 100", bg: "#faeeda", color: "#633806" },
  },
  {
    id: "c",
    name: "Jake Ryan",
    contact: "jake@email.com · (555) 000-1234 · github.com/jryan",
    edu: {
      school: "Southwestern University — B.S. Information Systems",
      years: "2018 – 2022",
    },
    exp: [
      {
        title: "Undergraduate Researcher · SWU Lab",
        years: "2022 – present",
        bars: ["f", "m", "s"],
      },
      {
        title: "IT Support Specialist · Campus IT",
        years: "2020 – 2022",
        bars: ["m", "s"],
      },
    ],
    skills: ["Java", "C++", "Linux", "Git", "Bash", "Kubernetes"],
    score: { val: "41 / 100", bg: "#fcebeb", color: "#791f1f" },
  },
];

const TONES = [
  "Professional",
  "Creative",
  "Technical",
  "Concise",
  "Enthusiastic",
];

export { CARDS, TONES };
