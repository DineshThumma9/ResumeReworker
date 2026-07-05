export type CardData = {
  id: string;
  name: string;
  contact: string;
  edu: { school: string; years: string };
  exp: { title: string; years: string; bars: ("s" | "m" | "f")[] }[];
  projects?: {
    title: string;
    year: string;
    bars: ("s" | "m" | "f")[];
    skills: string[];
  }[];
  skills?: string[];
  score: { val: string; bg: string; color: string };
};

const BAR_W = { s: "w-[48%]", m: "w-[72%]", f: "w-full" } as const;

export function ResumeCard({
  card,
  exitLeft,
  exitRight,
}: {
  card: CardData;
  exitLeft?: boolean;
  exitRight?: boolean;
}) {
  const posClass =
    card.id === "a"
      ? "left-[2%] top-[4%] -rotate-6 z-10"
      : card.id === "b"
        ? "left-[20%] top-[0%] rotate-1 z-20"
        : "left-[38%] top-[4%] rotate-6 z-30";

  const exitClass = exitLeft
    ? "!-left-[140%] ![clip-path:inset(0_100%_0_0_round_10px)] opacity-0"
    : exitRight
      ? "!left-[130%] ![clip-path:inset(0_0_0_100%_round_10px)] opacity-0"
      : "";

  return (
    <div
      className={`
        absolute w-[340px] xl:w-[400px] bg-white rounded-xl shadow-2xl
        px-7 py-7 flex flex-col gap-[6px]
        transition-all duration-700 ease-in-out
        [clip-path:inset(0_0_0_0_round_10px)]
        ${posClass} ${exitClass}
      `}
    >
      {/* name */}
      <div className="font-['EB_Garamond'] text-[19px] font-semibold text-[#1a1a1a] text-center tracking-[0.07em] uppercase">
        {card.name}
      </div>
      <div className="font-sans text-[10.5px] text-[#888] text-center leading-snug">
        {card.contact}
      </div>
      <hr className="border-t-[1.5px] border-[#1a1a1a] my-[6px]" />

      {/* Education */}
      <div className="font-['EB_Garamond'] text-[9.5px] font-bold tracking-[0.18em] uppercase text-[#1a1a1a] mb-[3px]">
        Education
      </div>
      <div className="flex justify-between items-baseline mb-[3px]">
        <span className="font-['EB_Garamond'] text-[13px] font-semibold text-[#1a1a1a] leading-snug">
          {card.edu.school}
        </span>
        <span className="font-sans text-[9.5px] text-[#bbb] ml-2 shrink-0">
          {card.edu.years}
        </span>
      </div>
      <div
        className={`h-[4px] bg-[#e8e8e8] rounded-full mb-[5px] ${BAR_W.m}`}
      />

      <hr className="border-t-[0.5px] border-[#e2e2e2] my-[3px]" />

      {/* Experience */}
      <div className="font-['EB_Garamond'] text-[9.5px] font-bold tracking-[0.18em] uppercase text-[#1a1a1a] mb-[3px]">
        Experience
      </div>
      {card.exp.map((e, i) => (
        <div key={i} className={i > 0 ? "mt-[7px]" : ""}>
          <div className="flex justify-between items-baseline mb-[3px]">
            <span className="font-['EB_Garamond'] text-[13px] font-semibold text-[#1a1a1a] leading-snug">
              {e.title}
            </span>
            <span className="font-sans text-[9.5px] text-[#bbb] ml-2 shrink-0">
              {e.years}
            </span>
          </div>
          {e.bars.map((b, j) => (
            <div
              key={j}
              className={`h-[4px] bg-[#e8e8e8] rounded-full mb-[4px] ${BAR_W[b]}`}
            />
          ))}
        </div>
      ))}

      {/* Projects */}
      {card.projects?.map((p, i) => (
        <div key={i} className="mt-[4px]">
          <hr className="border-t-[0.5px] border-[#e2e2e2] my-[4px]" />
          <div className="font-['EB_Garamond'] text-[9.5px] font-bold tracking-[0.18em] uppercase text-[#1a1a1a] mb-[3px]">
            Projects
          </div>
          <div className="flex justify-between items-baseline mb-[3px]">
            <span className="font-['EB_Garamond'] text-[13px] font-semibold text-[#1a1a1a]">
              {p.title}
            </span>
            <span className="font-sans text-[9.5px] text-[#bbb] ml-2 shrink-0">
              {p.year}
            </span>
          </div>
          {p.bars.map((b, j) => (
            <div
              key={j}
              className={`h-[4px] bg-[#e8e8e8] rounded-full mb-[3px] ${BAR_W[b]}`}
            />
          ))}
          <div className="flex gap-1.5 flex-wrap mt-[4px]">
            {p.skills.map((s) => (
              <span
                key={s}
                className="font-sans text-[9.5px] bg-[#f0f0f0] text-[#555] px-2 py-[3px] rounded-[3px]"
              >
                {s}
              </span>
            ))}
          </div>
        </div>
      ))}

      {/* Skills */}
      {card.skills && (
        <>
          <hr className="border-t-[0.5px] border-[#e2e2e2] my-[4px]" />
          <div className="font-['EB_Garamond'] text-[9.5px] font-bold tracking-[0.18em] uppercase text-[#1a1a1a] mb-[3px]">
            Technical Skills
          </div>
          <div className="flex gap-1.5 flex-wrap">
            {card.skills.map((s) => (
              <span
                key={s}
                className="font-sans text-[9.5px] bg-[#f0f0f0] text-[#555] px-2 py-[3px] rounded-[3px]"
              >
                {s}
              </span>
            ))}
          </div>
        </>
      )}

      {/* ATS score */}
      <div className="flex items-center justify-between mt-[8px] pt-[8px] border-t border-[#f0f0f0]">
        <span className="font-sans text-[9px] text-[#bbb] tracking-[0.05em] uppercase">
          ATS fit score
        </span>
        <span
          className="font-sans text-[12px] font-semibold px-3 py-1 rounded-[4px]"
          style={{ background: card.score.bg, color: card.score.color }}
        >
          {card.score.val}
        </span>
      </div>
    </div>
  );
}
