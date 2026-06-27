
export function BrandLogo({ large = false }: { large?: boolean }) {
  return (
    <div className="leading-none select-none">
      <span
        className={`font-heading text-white font-bold leading-tight block ${
          large ? "text-[52px] xl:text-[62px]" : "text-[40px] xl:text-[44px]"
        }`}
      >
        Resume Reworker
      </span>
      {/* <span
        className={`font-sans font-semibold tracking-widest uppercase text-[#b8d4a4] block ${
          large ? "text-[18px] xl:text-[22px]" : "text-[14px] xl:text-[16px]"
        }`} */}
      {/* >
        Reworker
      </span> */}
    </div>
  );
}
