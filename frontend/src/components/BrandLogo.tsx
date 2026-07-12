export function BrandLogo({ large = false }: { large?: boolean }) {
  return (
    <div className="leading-none select-none">
      <span
        className={`font-heading text-white font-bold leading-tight block ${
          large ? "text-[40px] md:text-[52px] xl:text-[62px]" : "text-[24px] md:text-[32px] lg:text-[40px] xl:text-[44px]"
        }`}
      >
        Resume Reworker
      </span>
    </div>
  );
}
