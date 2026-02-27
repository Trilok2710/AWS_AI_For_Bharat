import React from "react";

interface ButtonProps {
  label: string;
  onClick?: () => void;
  variant?: "primary" | "emergency" | "urgent" | "routine" | "secondary";
  type?: "button" | "submit";
  disabled?: boolean;
  fullWidth?: boolean;
}

const variantStyles: Record<string, string> = {
  primary: "bg-primary text-white",
  emergency: "bg-emergency text-white",
  urgent: "bg-urgent text-white",
  routine: "bg-routine text-white",
  secondary: "bg-white text-textPrimary border border-gray-300",
};

const Button: React.FC<ButtonProps> = ({
  label,
  onClick,
  variant = "primary",
  type = "button",
  disabled = false,
  fullWidth = true,
}) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        ${variantStyles[variant]}
        ${fullWidth ? "w-full" : ""}
        py-3 px-4
        text-sm font-medium
        border
        focus:outline-none
        transition-opacity
        ${disabled ? "opacity-50 cursor-not-allowed" : "hover:opacity-90"}
      `}
    >
      {label}
    </button>
  );
};

export default Button;