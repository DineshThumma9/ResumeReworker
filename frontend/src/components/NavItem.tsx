import React from "react";
import { NavLink } from "react-router-dom";

export function NavItem({
  to,
  icon,
  children,
  badge,
  onClick,
}: {
  to: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  badge?: number;
  onClick?: () => void;
}) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all ${
          isActive
            ? "bg-primary text-primary-foreground font-semibold shadow-sm"
            : "text-sidebar-foreground hover:bg-accent hover:text-accent-foreground"
        }`
      }
    >
      {icon}
      {children}
      {!!badge && badge > 0 && (
        <span className="ml-auto text-[11px] bg-primary/20 text-primary-foreground font-semibold px-2 py-0.5 rounded-full">
          {badge}
        </span>
      )}
    </NavLink>
  );
}
