import { ButtonHTMLAttributes, CSSProperties, ReactNode } from "react";

type ButtonVariant = "primary" | "ghost" | "danger" | "icon";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  iconSize?: number | string;
  variant?: ButtonVariant;
};

const baseClasses =
  `inline-flex min-h-10 items-center justify-center gap-2 rounded-lg px-4 text-sm font-bold transition-colors 
  disabled:cursor-not-allowed disabled:opacity-60 [&_svg]:h-[var(--button-icon-size)] 
  [&_svg]:w-[var(--button-icon-size)] [&_svg]:shrink-0`;
  
const variants: Record<ButtonVariant, string> = {
  primary: "text-sm bg-teal-700 text-white hover:bg-teal-800",
  ghost: "text-sm border border-slate-300 bg-white text-teal-700 hover:bg-slate-50 hover:text-teal-800",
  danger: "text-sm bg-red-700 text-white hover:bg-red-800",
  icon: "h-10 w-10 px-0 text-slate-500 hover:bg-slate-200 hover:text-slate-900",
};

export function Button({
  children,
  className = "",
  iconSize = 20,
  style,
  variant = "primary",
  ...props
}: ButtonProps) {
  const buttonStyle = {
    "--button-icon-size": typeof iconSize === "number" ? `${iconSize}px` : iconSize,
    ...style,
  } as CSSProperties;

  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${className}`}
      style={buttonStyle}
      {...props}
    >
      {children}
    </button>
  );
}
