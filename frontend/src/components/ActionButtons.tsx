/* ── small action button ─────────────────────────────────────────── */
export function ActionBtn({
  icon,
  label,
  onClick,
  accent = false,
  ghost = false,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  accent?: boolean;
  ghost?: boolean;
}) {
  const base =
    "flex items-center gap-1.5 text-[11px] font-semibold px-3 py-1.5 rounded-md border cursor-pointer transition-all duration-150 select-none";
  const style = accent
    ? "bg-primary text-white border-primary hover:bg-primary/90 shadow-sm"
    : ghost
      ? "bg-transparent text-muted-foreground border-transparent hover:bg-black/6 dark:hover:bg-white/8"
      : "bg-white dark:bg-[#333] text-foreground border-black/10 dark:border-white/10 hover:border-primary/40 hover:shadow-sm";
  return (
    <button className={`${base} ${style}`} onClick={onClick}>
      {icon}
      {label}
    </button>
  );
}
