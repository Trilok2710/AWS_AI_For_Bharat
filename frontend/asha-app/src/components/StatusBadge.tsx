import React from "react";

interface StatusBadgeProps {
  status: "EMERGENCY" | "URGENT" | "ROUTINE";
}

const statusStyles: Record<string, string> = {
  EMERGENCY: "bg-emergency text-white",
  URGENT: "bg-urgent text-white",
  ROUTINE: "bg-routine text-white",
};

const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  return (
    <span
      className={`
        ${statusStyles[status]}
        text-xs
        font-semibold
        px-2
        py-1
        tracking-wide
      `}
    >
      {status}
    </span>
  );
};

export default StatusBadge;