import React from "react";

interface HeaderProps {
  title?: string;
  subtitle?: string;
  showBack?: boolean;
  onBack?: () => void;
}

const Header: React.FC<HeaderProps> = ({
  title = "MediConnect",
  subtitle,
  showBack = false,
  onBack,
}) => {
  return (
    <header className="bg-primary text-white border-b border-gray-300">
      <div className="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
        
        {/* Left Section */}
        <div className="flex items-center space-x-3">
          {showBack && (
            <button
              onClick={onBack}
              className="text-sm font-medium opacity-90 hover:opacity-100"
            >
              Back
            </button>
          )}

          <div>
            <h1 className="text-lg font-semibold tracking-tight">
              {title}
            </h1>
            {subtitle && (
              <p className="text-xs opacity-80">
                {subtitle}
              </p>
            )}
          </div>
        </div>

        {/* Right Section Placeholder (language toggle later) */}
        <div />
      </div>
    </header>
  );
};

export default Header;