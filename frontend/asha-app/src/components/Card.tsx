import React from "react";

interface CardProps {
  children: React.ReactNode;
  onClick?: () => void;
  padding?: "none" | "sm" | "md" | "lg";
}

const paddingStyles = {
  none: "",
  sm: "p-3",
  md: "p-4",
  lg: "p-6",
};

const Card: React.FC<CardProps> = ({
  children,
  onClick,
  padding = "md",
}) => {
  return (
    <div
      onClick={onClick}
      className={`
        bg-white
        border border-gray-200
        ${paddingStyles[padding]}
        ${onClick ? "cursor-pointer hover:bg-gray-50 transition-colors" : ""}
      `}
    >
      {children}
    </div>
  );
};

export default Card;